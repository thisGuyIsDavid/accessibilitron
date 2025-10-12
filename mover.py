import paramiko

# Define SFTP connection parameters
hostname = '192.168.86.240'
port = 22  # Default SFTP port
username = 'pi'

ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy()) # Or use WarningPolicy for stricter security

# Connect using password
ssh_client.connect(hostname='192.168.86.240', username='pi', password='raspberry')

sftp_client = ssh_client.open_sftp()

local_file_path = '/Users/davidhaverberg/PycharmProjects/accessibilitron/main.py'
remote_file_path = '/home/pi/api/main.py'
sftp_client.put(local_file_path, remote_file_path)
sftp_client.close()
ssh_client.close()
