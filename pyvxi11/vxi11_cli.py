#!/usr/bin/env python
#
# Simple VXI-11 commandline interface
# Copyright (c) 2011 Michael Walle
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Description:
# Commands are sent to the VXI-11 device after every newline. If the command
# ends in '?' the response is received.
#

import os.path
import time
import sys
import logging
from optparse import OptionParser

from pyvxi11 import Vxi11, Vxi11Error, __version__

# Use correct input method for Python 3
if sys.version_info.major == 3:
    raw_input = input

LOCAL_COMMANDS = {
        '%SLEEP': (1, 1, lambda a: time.sleep(float(a[0])/1000)),
}


def process_local_command(cmd):
    args = cmd.split()
    if args[0] in LOCAL_COMMANDS:
        cmd_info = LOCAL_COMMANDS[args[0]]
        if cmd_info[0] <= len(args[1:]) <= cmd_info[1]:
            cmd_info[2](args[1:])
        else:
            print('Invalid number of arguments for command {}'.format(args[0]))
    else:
        print('Unknown command "{}"'.format(cmd))

        
def main():
    usage = 'usage: %prog [options] <host>'
    parser = OptionParser(usage=usage)
    parser.add_option('-d', action='store_true', dest='debug',
                      help='enable debug messages')
    parser.add_option('-v', action='store_true', dest='verbose',
                      help='be more verbose')
    parser.add_option('-V', action='store_true', dest='version',
                      help='show version')
    parser.add_option('--always-check-esr', action='store_true',
                      dest='check_esr',
                      help='Check the error status register after every command')

    (options, args) = parser.parse_args()

    if options.version:
        print('{} v{}'.format(os.path.basename(sys.argv[0]), __version__))
        sys.exit(0)

    logging.basicConfig()
    if options.verbose:
        logging.getLogger('pyvxi11').setLevel(logging.INFO)
    if options.debug:
        logging.getLogger('pyvxi11').setLevel(logging.DEBUG)

    if len(args) < 1:
        print(parser.format_help())
        sys.exit(1)

    host = args[0]

    v = Vxi11(host)
    v.open()

    print("Enter command to send. Quit with 'q'.")

    try:
        while True:
            cmd = raw_input('=> ')
            if cmd == 'q':
                break
            if cmd.startswith('%'):
                process_local_command(cmd)
                continue
            if len(cmd) > 0:
                is_query = cmd.split(' ')[0][-1] == '?'
                try:
                    if is_query:
                        print(v.ask(cmd).decode())
                    else:
                        v.write(cmd)
                    if options.check_esr:
                        esr = int(v.ask('*ESR?').strip())
                        if esr != 0:
                            print('Warning: ESR was {}'.format(esr))
                except Vxi11Error as e:
                    print('ERROR: {}'.format(e))
    except EOFError:
        print('exitting..')

    v.close()


if __name__ == '__main__':
    main()
