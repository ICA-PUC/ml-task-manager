"""Remote Operations Handler class for ssh connection and scp file transfer"""
import hashlib
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient


class RemoteHandler:
    """Paramiko and scp based remote handler class"""

    def __init__(self):
        self.stdin = ""
        self.stdout = ""
        self.stderr = ""

        self.client = SSHClient()
        self.client.load_system_host_keys()
        self.client.set_missing_host_key_policy(AutoAddPolicy())

    def _assert_integrity(self, filename):
        """Assert local and remote file integrity"""
        filepath = f"app/tmp/{filename}"
        with open(filepath, 'r', encoding='utf-8') as f:
            local_hash = hashlib.md5(str(f.read()).encode('utf-8')).hexdigest()
        self.exec(f"md5sum /tmp/{filename}")
        remote_hash = self.get_output()
        remote_hash = remote_hash.split(" ")[0]
        if local_hash == remote_hash:
            return True
        return False

    def connect(self,  host, user, passwd):
        """Connect to SSH host"""
        self.client.connect(
            hostname=host, username=user, password=passwd)

    def close(self):
        """SSH close connection call"""
        self.client.close()

    def exec(self, command):
        """Execute command given"""
        stdin, stdout, stderr = self.client.exec_command(command)
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def get_output(self):
        """Get standard output of latest command executed"""
        return self.stdout.read().decode('utf8')

    def send_file(self, filename):
        """Send file via scp"""
        scp = SCPClient(self.client.get_transport())
        local_path = f"app/tmp/{filename}"
        remote_path = f"/tmp/{filename}"
        scp.put(local_path, remote_path)
        scp.close()
        sanity_check = self._assert_integrity(filename)
        return sanity_check
