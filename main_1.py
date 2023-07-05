import paramiko

def get_authorized_keys(hostname, username):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname, username=username)
        ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command('cat ~/.ssh/authorized_keys')
        authorized_keys = ssh_stdout.read().decode('utf-8').split('\n')
        return authorized_keys
    except Exception as e:
        print(f"Error occurred while retrieving authorized keys from {hostname}: {str(e)}")
    finally:
        client.close()

def remove_authorized_key(hostname, username, key_to_remove):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        client.connect(hostname, username=username)
        ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command('cat ~/.ssh/authorized_keys')
        authorized_keys = ssh_stdout.read().decode('utf-8').split('\n')
        if key_to_remove in authorized_keys:
            authorized_keys.remove(key_to_remove)
            updated_keys = '\n'.join(authorized_keys)

            ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command(f'echo "{updated_keys}" > ~/.ssh/authorized_keys')
            if ssh_stdout.channel.recv_exit_status() == 0:
                print(f"SSH key removed from {hostname}")
            else:
                print(f"Failed to remove SSH key from {hostname}")
        else:
            print(f"SSH key not found on {hostname}")
    except Exception as e:
        print(f"Error occurred while removing SSH key from {hostname}: {str(e)}")
    finally:
        client.close()

# 检测已建立的互信关系，自动获取主机名、用户名和要删除的公钥
def detect_ssh_trust():
    client = paramiko.SSHClient()
    client.load_system_host_keys()

    try:
        client.connect('localhost')
        ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command('hostname')
        hostname = ssh_stdout.read().decode('utf-8').strip()

        ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command('whoami')
        username = ssh_stdout.read().decode('utf-8').strip()

        authorized_keys = get_authorized_keys(hostname, username)

        return hostname, username, authorized_keys
    except Exception as e:
        print(f"Error occurred while detecting SSH trust: {str(e)}")
    finally:
        client.close()

# 获取当前主机的连接信息
host_hostname, host_username, host_authorized_keys = detect_ssh_trust()

# 从机列表的连接信息
slaves = [
    {
        'hostname': 'slave1.example.com',
        'username': 'your_username',
        'key_to_remove': host_key
    },
    {
        'hostname': 'slave2.example.com',
        'username': 'your_username',
        'key_to_remove': host_key
    },
    # ...
]

# 从主机中移除从机的公钥
for slave in slaves:
    remove_authorized_key(host_hostname, host_username, slave['key_to_remove'])
    # 从从机中移除主机的公钥
    remove_authorized_key(slave['hostname'], slave['username'], host_authorized_keys)