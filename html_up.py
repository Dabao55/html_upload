import paramiko
import time


def connect(ID: str, username, password, port=22):
    '''
    该函数用于连接服务器，包括SSH和SFTP

    :param ID: 云服务器的公网id
    :param username: 登陆用的用户名
    :param password: 密码
    :param port: ssh远控端口，默认22
    :return: None
    '''
    # SFTP 和 SSH连接
    SFTP_hostname = ID
    SFTP_port = port

    SSH_hostname = ID
    SSH_port = port

    while True:
        try:
            global t
            t = paramiko.Transport((SFTP_hostname, SFTP_port))
            t.connect(username=username, password=password)
            print('\n SFTP Connect successfully, congratulation!')

            global s
            s = paramiko.SSHClient()
            s.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            s.connect(SSH_hostname, SSH_port, username=username, password=password)
            print('\n SSH Connect successfully, congratulation!')

            break
        except:
            print('\n username or password error, please try again!')


# 定义一个ssh函数
def command(argu):
    # 打开一个Channel并执行命令
    stdin, stdout, stderr = s.exec_command(argu)  # stdout 为正确输出，stderr为错误输出，同时是有1个变量有值

    # 打印执行结果
    result1 = stdout.read().decode('utf-8')
    result2 = stderr.read().decode('utf-8')
    print(stdout.read().decode('utf-8'), stderr.read().decode('utf-8'))

    return (result1, result2)


def main(webport: int, htmlzippath: str):
    '''
    将本地网页打包成zip文件后一键上传到云服务器的docker容器

    :param webport: 容器内部80端口映射主机的端口
    :param htmlzippath: zip文件地址  形如 'C:/Users/admin/Desktop/test.zip'
    :return: None
    '''
    port = webport
    local_file = htmlzippath
    # create container
    date = time.strftime("%Y%m%d%H%M%S")
    name = 'nginx' + date
    print(command(f'docker run -d --name {name} -p {str(port)}:80 nginx:latest'))
    print(f'container {name} is creating, please wait 5 seconds!')
    time.sleep(5)

    # upload files
    sftp = paramiko.SFTPClient.from_transport(t)
    print(command(f'mkdir /root/temp{name}'))
    filename = local_file.split('/')[-1].split('.')[0]
    remote_file = f'/root/temp{name}/temp.zip'
    sftp.put(local_file, remote_file)
    print(command(f'unzip {remote_file} -d /root/temp{name}/'))
    print('file {} upload to {} successfully!'.format(local_file, remote_file))

    # transport to container
    print(command(f'docker cp /root/temp{name}/{filename} {name}:/usr/share/nginx/html/'))
    print(command(f'rm -rf /root/temp{name}'))
    print(f'\n\nplease open the chrome browser and visit URL:\n{ID}:{port}/{filename}/index.html')


if __name__ == '__main__':
    ID = 'blog0722.xyz'
    username = input('Please input username:')
    password = input('Please input password:')
    webport = 6333
    htmlzippath = 'C:/Users/Jiawen Shen/Desktop/whu.zip'  # 'C:/Users/admin/Desktop/test.zip'
    connect(ID, username, password)
    main(webport, htmlzippath)
