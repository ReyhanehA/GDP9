import socket
import struct

import riak.pb.riak_pb2
import riak.pb.messages

from riak import RiakError
from riak.codecs.pbuf import PbufCodec
from riak.security import SecurityError, USE_STDLIB_SSL

if not USE_STDLIB_SSL:
    from OpenSSL.SSL import Connection
    from riak.transports.security import configure_pyopenssl_context
else:
    import ssl
    from riak.transports.security import configure_ssl_context


class TcpConnection(object):
    """
    Connection-related methods for TcpTransport.
    """
    def _encode_msg(self, msg_code, data=None):
        if data is None:
            return struct.pack("!iB", 1, msg_code)
        hdr = struct.pack("!iB", 1 + len(data), msg_code)
        return hdr + data

    def _send_recv(self, msg_code, data=None):
        self._send_msg(msg_code, data)
        return self._recv_msg()

    def _non_connect_send_recv(self, msg_code, data=None):
        """
        Similar to self._send_recv, but doesn't try to initiate a connection,
        thus preventing an infinite loop.
        """
        self._non_connect_send_msg(msg_code, data)
        return self._recv_msg()

    def _non_connect_send_recv_msg(self, msg):
        self._non_connect_send_msg(msg.msg_code, msg.data)
        return self._recv_msg()

    def _non_connect_send_msg(self, msg_code, data):
        """
        Similar to self._send, but doesn't try to initiate a connection,
        thus preventing an infinite loop.
        """
        self._socket.sendall(self._encode_msg(msg_code, data))

    def _send_msg(self, msg_code, data):
        self._connect()
        self._non_connect_send_msg(msg_code, data)

    def _init_security(self):
        """
        Initialize a secure connection to the server.
        """
        if not self._starttls():
            raise SecurityError("Could not start TLS connection")
        # _ssh_handshake() will throw an exception upon failure
        self._ssl_handshake()
        if not self._auth():
            raise SecurityError("Could not authorize connection")

    def _starttls(self):
        """
        Exchange a STARTTLS message with Riak to initiate secure communications
        return True is Riak responds with a STARTTLS response, False otherwise
        """
        resp_code, _ = self._non_connect_send_recv(
            riak.pb.messages.MSG_CODE_START_TLS)
        if resp_code == riak.pb.messages.MSG_CODE_START_TLS:
            return True
        else:
            return False

    def _auth(self):
        """
        Perform an authorization request against Riak
        returns True upon success, False otherwise
        Note: Riak will sleep for a short period of time upon a failed
              auth request/response to prevent denial of service attacks
        """
        codec = PbufCodec()
        username = self._client._credentials.username
        password = self._client._credentials.password
        if not password:
            password = ''
        msg = codec.encode_auth(username, password)
        resp_code, _ = self._non_connect_send_recv_msg(msg)
        if resp_code == riak.pb.messages.MSG_CODE_AUTH_RESP:
            return True
        else:
            return False

    if not USE_STDLIB_SSL:
        def _ssl_handshake(self):
            """
            Perform an SSL handshake w/ the server.
            Precondition: a successful STARTTLS exchange has
                         taken place with Riak
            returns True upon success, otherwise an exception is raised
            """
            if self._client._credentials:
                try:
                    ssl_ctx = configure_pyopenssl_context(self.
                                                          _client._credentials)
                    # attempt to upgrade the socket to SSL
                    ssl_socket = Connection(ssl_ctx, self._socket)
                    ssl_socket.set_connect_state()
                    ssl_socket.do_handshake()
                    # ssl handshake successful
                    self._socket = ssl_socket

                    self._client._credentials._check_revoked_cert(ssl_socket)
                    return True
                except Exception as e:
                    # fail if *any* exceptions are thrown during SSL handshake
                    raise SecurityError(e)
    else:
        def _ssl_handshake(self):
            """
            Perform an SSL handshake w/ the server.
            Precondition: a successful STARTTLS exchange has
                         taken place with Riak
            returns True upon success, otherwise an exception is raised
            """
            credentials = self._client._credentials
            if credentials:
                try:
                    ssl_ctx = configure_ssl_context(credentials)
                    host = self._address[0]
                    ssl_socket = ssl.SSLSocket(sock=self._socket,
                                               keyfile=credentials.pkey_file,
                                               certfile=credentials.cert_file,
                                               cert_reqs=ssl.CERT_REQUIRED,
                                               ca_certs=credentials.
                                               cacert_file,
                                               ciphers=credentials.ciphers,
                                               server_hostname=host)
                    ssl_socket.context = ssl_ctx
                    # ssl handshake successful
                    ssl_socket.do_handshake()
                    self._socket = ssl_socket
                    return True
                except ssl.SSLError as e:
                    raise SecurityError(e)
                except Exception as e:
                    # fail if *any* exceptions are thrown during SSL handshake
                    raise SecurityError(e)

    def _recv_msg(self):
        msgbuf = self._recv_pkt()
        mv = memoryview(msgbuf)
        msg_code, = struct.unpack("B", mv[0:1])
        data = mv[1:].tobytes()
        return (msg_code, data)

    def _recv_pkt(self):
        # TODO FUTURE re-use buffer
        msglen_buf = self._recv(4)
        # NB: msg length is an unsigned int
        msglen, = struct.unpack('!I', msglen_buf)
        return self._recv(msglen)

    def _recv(self, msglen):
        # TODO FUTURE re-use buffer
        # http://stackoverflow.com/a/15964489
        msgbuf = bytearray(msglen)
        view = memoryview(msgbuf)
        nread = 0
        toread = msglen
        while toread:
            nbytes = self._socket.recv_into(view, toread)
            view = view[nbytes:]  # slicing views is cheap
            toread -= nbytes
            nread += nbytes
        if nread != msglen:
            raise RiakError("Socket returned short packet %d - expected %d"
                            % (nread, msglen))
        return msgbuf

    def _connect(self):
        if not self._socket:
            if self._timeout:
                self._socket = socket.create_connection(self._address,
                                                        self._timeout)
            else:
                self._socket = socket.create_connection(self._address)
            if self._client._credentials:
                self._init_security()

    def close(self):
        """
        Closes the underlying socket of the PB connection.
        """
        if self._socket:
            self._socket.close()
            del self._socket

    # These are set in the TcpTransport initializer
    _address = None
    _timeout = None
