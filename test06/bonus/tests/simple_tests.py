import unittest
import logging
import socket
import ipaddress
import os
import sys
import subprocess
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import script.script as script


class UnitTest(unittest.TestCase):

    logfile = logger = socks = None

    @classmethod
    def setUpClass(cls):
        cls.logfile = '{}/file.log'.format(sys.path[-1])
        cls.logger = script.conf_log(cls.logfile)
        ports = [11111]
        cls.socks = script.open_sockets(ports=ports)

    def test_logger(self):
        self.assertIsInstance(self.logger, logging.Logger)
        self.assertTrue(os.path.exists(self.logfile))
        self.assertLogs(self.logger, logging.INFO)

    def test_sockets(self):
        self.assertIsInstance(self.socks, list)
        self.assertGreater(len(self.socks), 0)
        for sock in self.socks:
            self.assertIsInstance(sock, socket.socket)

    @classmethod
    def tearDownClass(cls):
        for sock in cls.socks:
            sock.close()
        os.unlink(cls.logfile)


class FuncTest(unittest.TestCase):

    def setUp(self):
        self.sp = None
        self.script = '{}/script/script.py'.format(sys.path[-1])
        self.ports = [11111, 11112]
        self.logfile = '{}/file.log'.format(sys.path[-1])

    def test_open(self):
        self.sp = subprocess.Popen(['python3', self.script,
                                    '--ports', '{},'.format(self.ports[0]),
                                    '--logfile', self.logfile])
        self.assertTrue(self.sp.pid)
        time.sleep(0.5)
        curl = subprocess.run(['curl', '-s', 'localhost:{}'.format(self.ports[0])])
        self.assertIn(curl.returncode, [52, 56])
        with open(self.logfile) as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)
            self.assertTrue(ipaddress.ip_address(lines[0].split('-')[-1].strip()))

    def test_two_open(self):
        self.sp = subprocess.Popen(['python3', self.script,
                                    '--ports', ','.join(str(item) for item in self.ports),
                                    '--logfile', self.logfile])
        self.assertTrue(self.sp.pid)
        time.sleep(0.5)
        for port in self.ports:
            curl = subprocess.run(['curl', '-s', 'localhost:{}'.format(port)])
            self.assertIn(curl.returncode, [52, 56])
        with open(self.logfile) as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)
            for line in lines:
                self.assertTrue(ipaddress.ip_address(line.split('-')[-1].strip()))

    def tearDown(self):
        self.sp.terminate()
        self.sp.wait()
        os.unlink(self.logfile)


if __name__ == '__main__':
    unittest.main()

