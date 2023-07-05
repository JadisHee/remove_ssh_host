import paramiko

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

# 主机的连接信息
host = {
    'hostname': 'host.example.com',
    'username': 'your_username',
    'keys_to_remove': [
        'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDXdxK1...',
        'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDXdxK2...',
        'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDXdxK3...'
    ]
}

# 从机列表的连接信息
slaves = [
    {
        'hostname': 'slave1.example.com',
        'username': 'your_username',
        'key_to_remove': 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDXdxK1...'
    },
    {
        'hostname': 'slave2.example.com',
        'username': 'your_username',
        'key_to_remove': 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDXdxK2...'
    },
    {
        'hostname': 'slave3.example.com',
        'username': 'your_username',
        'key_to_remove': 'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDXdxK3...'
    }
]

# 取消主机与从机之间的互信关系
for slave in slaves:
    remove_authorized_key(host['hostname'], host['username'], slave['key_to_remove'])
    remove_authorized_key(slave['hostname'], slave['username'], host['keys_to_remove'])
