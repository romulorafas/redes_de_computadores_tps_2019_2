# Python bytecode 3.5 (3350)
# Decompiled from: Python 2.7.15 (default, May  1 2018, 16:44:08)
# [GCC 4.2.1 Compatible Apple LLVM 9.1.0 (clang-902.0.39.1)]
# Embedded file name: router.py
# Compiled at: 2018-05-30 18:55:14
# Size of source mod 2**32: 11933 bytes
import argparse, ipaddress, json, logging, random, resource, selectors, socket, sys, time
from collections import defaultdict, namedtuple
opts = None
MSGTYPE_UPDATE = 'update'
MSGTYPE_TRACE = 'trace'
MSGTYPE_DATA = 'data'
MSGFLD_TYPE = 'type'
MSGFLD_SRC = 'source'
MSGFLD_DST = 'destination'
MSGFLD_HOPS = 'hops'
MSGFLD_PAYLOAD = 'payload'
MSGFLD_DIST = 'distances'
MANDATORY_MESSAGE_FIELDS = frozenset([MSGFLD_TYPE, MSGFLD_SRC, MSGFLD_DST])

class RoutingTable:
    Entry = namedtuple('Entry', ['dist', 'tstamp'])

    def __init__(self, addr):
        self.addr = addr
        self.dst2nhop2entry = defaultdict(dict)

    def __getitem__(self, dst):
        self.remove_expired_entries()
        if dst not in self.dst2nhop2entry:
            return
        nhop2entry = self.dst2nhop2entry[dst]
        min_distance = min((e.dist for e in nhop2entry.values()))
        return random.choice([nhop for nhop, e in nhop2entry.items() if e.dist == min_distance])

    def remove_expired_entries(self):
        global opts
        now = time.time()
        dst2nhop2entry = defaultdict(dict)
        for dst, nhop2entry in self.dst2nhop2entry.items():
            for nhop, entry in nhop2entry.items():
                if now - entry.tstamp > opts.max_route_age:
                    logging.info('route to %s through %s expired', dst, nhop)
                else:
                    dst2nhop2entry[dst][nhop] = entry

        self.dst2nhop2entry = dst2nhop2entry

    def drop_nexthop(self, neigh):
        dst2nhop2entry = defaultdict(dict)
        for dst, nhop2entry in self.dst2nhop2entry.items():
            nhop2entry = {nhop:e for nhop, e in nhop2entry.items() if nhop != neigh}
            if nhop2entry:
                dst2nhop2entry[dst] = nhop2entry

        self.dst2nhop2entry = dst2nhop2entry

    def update(self, dst2distance, neigh, weight):
        if dst2distance.pop(self.addr, None) is not None:
            logging.error('received route to self from %s', neigh)
            return
        logging.info('processing routes to %d destinations through %s', len(dst2distance), neigh)
        for dst, dist in dst2distance.items():
            if not dst != self.addr:
                raise AssertionError
            entry = RoutingTable.Entry(dist + weight, time.time())
            self.dst2nhop2entry[dst][neigh] = entry

    def get_dst2distance_split_horizon(self, neigh):
        self.remove_expired_entries()
        dst2dist = dict()
        dst2dist[self.addr] = 0
        for dst, nhop2entry in self.dst2nhop2entry.items():
            if dst == neigh:
                continue
            entries = list((e for h, e in nhop2entry.items() if h != neigh))
            if entries:
                dst2dist[dst] = min((e.dist for e in entries))

        return dst2dist


class Router:

    def __init__(self, addr):
        self.addr = addr
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        self.sock.bind((addr, opts.port))
        self.neigh2weight = dict()
        self.rtable = RoutingTable(addr)

    def add_link(self, neigh, weight):
        if neigh in self.neigh2weight:
            logging.error('link to %s already exists, ignoring', neigh)
            sys.stdout.write('link to %s already exists, ignoring.\n' % neigh)
            return
        self.neigh2weight[neigh] = weight
        self.send_update(neigh)

    def del_link(self, neigh):
        if neigh not in self.neigh2weight:
            logging.error('no link to %s, ignoring', neigh)
            sys.stdout.write('no link to %s, ignoring\n' % neigh)
            return
        del self.neigh2weight[neigh]
        self.rtable.drop_nexthop(neigh)

    def route(self, msgdata):
        msgstr = json.dumps(msgdata)
        dst = msgdata[MSGFLD_DST]
        if dst == self.addr:
            logging.info('message from %s: %s', msgdata[MSGFLD_SRC], msgdata[MSGFLD_PAYLOAD])
            sys.stdout.write('message from %s:\n' % msgdata[MSGFLD_SRC])
            sys.stdout.write('%s\n' % msgdata[MSGFLD_PAYLOAD])
            return
        nexthop = self.rtable[dst]
        print (self.rtable.dst2nhop2entry.items())
        if nexthop is None:
            logging.error('destination %s unreachable, dropping message: %s', dst, msgstr)
            return
        self.sock.sendto(msgstr.encode('utf-8'), (nexthop, opts.port))

    def process_message(self):
        data, address = self.sock.recvfrom(65535)
        # print ("address:",address)
        # print ("data:",data)
        neigh, _port = address
        # print ("self.neigh2weight:", self.neigh2weight)
        if neigh not in self.neigh2weight:
            logging.error('message from %s; not a neighbor, ignoring', neigh)
            return
        try:
            msgdata = json.loads(data.decode('utf-8'))
        except ValueError:
            logging.error('malformed JSON received from %s, ignoring', neigh)
            return

        if not MANDATORY_MESSAGE_FIELDS.issubset(set(msgdata.keys())):
            logging.error('message from %s missing mandatory fields: %s', neigh, msgdata)
            return
        if msgdata[MSGFLD_TYPE] == MSGTYPE_UPDATE:
            self.process_update(msgdata)
        else:
            if msgdata[MSGFLD_TYPE] == MSGTYPE_TRACE:
                self.process_trace(msgdata)
            else:
                if msgdata[MSGFLD_TYPE] == MSGTYPE_DATA:
                    self.route(msgdata)
                else:
                    logging.error('unknown message type from %s: %s', neigh, msgdata)

    def process_update(self, msgdata):
        if not msgdata[MSGFLD_TYPE] == MSGTYPE_UPDATE:
            raise AssertionError
        if not msgdata[MSGFLD_SRC] in self.neigh2weight:
            raise AssertionError
        neigh = msgdata[MSGFLD_SRC]

        # print ("msgdata[MSGFLD_DST] != self.addr:", msgdata[MSGFLD_DST] != self.addr)
        # print ("not isinstance(msgdata[MSGFLD_DIST], dict):", not isinstance(msgdata[MSGFLD_DIST], dict))
        # print ("TYPE msgdata[MSGFLD_DIST]:", type(msgdata[MSGFLD_DIST]))
        if msgdata[MSGFLD_DST] != self.addr or not isinstance(msgdata[MSGFLD_DIST], dict):
            # print ("to no process_update")
            logging.error('malformed update from %s: %s', neigh, msgdata)
            return
        dst2distance = msgdata[MSGFLD_DIST]
        logging.error('update received from %s: %s', neigh, msgdata)
        self.rtable.update(dst2distance, neigh, self.neigh2weight[neigh])

    def process_trace(self, msgdata):
        if not msgdata[MSGFLD_TYPE] == MSGTYPE_TRACE:
            raise AssertionError
        src = msgdata[MSGFLD_SRC]
        dst = msgdata[MSGFLD_DST]
        msgdata[MSGFLD_HOPS].append(self.addr)
        if dst == self.addr:
            logging.info('terminating trace from %s: %s', src, msgdata[MSGFLD_HOPS])
            payload = json.dumps(msgdata)
            msgdata = {MSGFLD_TYPE: MSGTYPE_DATA,
             MSGFLD_SRC: self.addr,
             MSGFLD_DST: src,
             MSGFLD_PAYLOAD: payload}
        self.route(msgdata)

    def send_all_updates(self):
        for neigh in self.neigh2weight:
            self.send_update(neigh)

    def send_update(self, neigh):
        dst2dist = self.rtable.get_dst2distance_split_horizon(neigh)
        logging.info('sending update to %s: %s', neigh, dst2dist)
        msgdata = {MSGFLD_TYPE: MSGTYPE_UPDATE,
         MSGFLD_SRC: self.addr,
         MSGFLD_DST: neigh,
         MSGFLD_DIST: dst2dist}
        msgstr = json.dumps(msgdata, indent=2)
        self.sock.sendto(msgstr.encode('utf-8'), (neigh, opts.port))

    def send_trace(self, dst):
        msgdata = {MSGFLD_TYPE: MSGTYPE_TRACE,
         MSGFLD_SRC: self.addr,
         MSGFLD_DST: dst,
         MSGFLD_HOPS: list()}
        self.process_trace(msgdata)


class CLI:

    def __init__(self, router):
        self.router = router
        sys.stdout.write('> ')
        sys.stdout.flush()

    def process_input(self):
        line = sys.stdin.readline()
        self.process_command(line)
        sys.stdout.write('> ')
        sys.stdout.flush()

    def process_command(self, cmdline):
        if cmdline.startswith('help'):
            sys.stdout.write('commands:\n')
            sys.stdout.write('add neighbor weight  (add 127.0.1.2 13)\n')
            sys.stdout.write('del neighbor         (del 127.0.1.2)\n')
            sys.stdout.write('trace destination    (trace 127.0.1.7)\n')
        else:
            if cmdline.startswith('add'):
                _cmd, neigh, weight = cmdline.split()
                try:
                    neigh = ipaddress.IPv4Address(neigh)
                except ValueError:
                    sys.stdout.write('failed to parse %s into an IPv4\n' % neigh)
                    return

                try:
                    weight = int(weight)
                except ValueError:
                    sys.stdout.write('failed to parse %s into an int\n')
                    return

                if int(weight) <= 0:
                    sys.stdout.write('weight must be larger than 0\n')
                    return
                self.router.add_link(str(neigh), weight)
            else:
                if cmdline.startswith('del'):
                    _cmd, neigh = cmdline.split()
                    try:
                        neigh = ipaddress.IPv4Address(neigh)
                    except ValueError:
                        sys.stdout.write('failed to parse %s into an IPv4\n' % neigh)
                        return

                    self.router.del_link(str(neigh))
                else:
                    if cmdline.startswith('trace'):
                        _cmd, dst = cmdline.split()
                        try:
                            dst = ipaddress.IPv4Address(dst)
                        except ValueError:
                            sys.stdout.write('failed to parse %s into an IPv4\n' % dst)
                            return

                        self.router.send_trace(str(dst))
                    else:
                        if cmdline.startswith('quit'):
                            sys.exit(1)


def create_parser():
    desc = 'DCCRIP router'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--addr', dest='addr', metavar='IPV4', type=str, required=True, help='IPv4 address to listen on (usually inside 127.0.1.0/24)')
    parser.add_argument('--port', dest='port', metavar='PORT', type=int, required=False, help='UDP port to listen on [%(default)s]', default=55152)
    parser.add_argument('--update-period', dest='update_period', metavar='SECS', type=float, required=False, help='Period between updates [%(default)s]', default=2.0)
    parser.add_argument('--startup-commands', dest='startup_commands_fn', metavar='FILE', type=str, required=False, help='File to read startup commands from')
    return parser


def main():
    global opts
    resource.setrlimit(resource.RLIMIT_AS, (1073741824, 1073741824))
    resource.setrlimit(resource.RLIMIT_FSIZE, (34359738368, 34359738368))
    parser = create_parser()
    opts = parser.parse_args()
    opts.max_route_age = 4 * opts.update_period
    logging.basicConfig(filename='log-%s.txt' % opts.addr, format='%(asctime)s %(funcName)s: %(message)s', level=logging.DEBUG)
    router = Router(opts.addr)
    cli = CLI(router)
    if opts.startup_commands_fn:
        with open(opts.startup_commands_fn) as (fd):
            for line in fd:
                cli.process_command(line)

    selector = selectors.DefaultSelector()
    selector.register(router.sock, selectors.EVENT_READ, router.process_message)
    selector.register(sys.stdin, selectors.EVENT_READ, cli.process_input)
    next_update = time.time() + opts.update_period
    while True:
        remaining_timeout = next_update - time.time()
        if remaining_timeout < 0:
            router.send_all_updates()
            next_update += opts.update_period
            remaining_timeout = next_update - time.time()
        events = selector.select(timeout=remaining_timeout)
        for key, _mask in events:
            callback = key.data
            callback()

    selector.close()


if __name__ == '__main__':
    sys.exit(main())
# okay decompiling router.pyc
