import argparse
import logging
import signal
import sys

from .fan import Fan


def parse_args():
    parser = argparse.ArgumentParser()
    # nargs参数的妙用
    # add参数是可选的，但是我也想不加-a时且没有其他参数时也执行这个动作
    # 或者一个nagrs=*的positional，但是也可以不提供
    parser.add_argument('-n', '--new', metavar='X', nargs='*', help='发布新的状态')
    parser.add_argument('-i', '--image', help='添加图片')
    parser.add_argument('-r', '--revert', action='store_true', help='撤回前一条消息')
    parser.add_argument('-s', '--save_all_statuses', nargs='?', const='timeline.json', help='备份所有状态为JSON格式,输入保存文件名')
    parser.add_argument('-p', '--protect', metavar='0/1', type=int, help='需要我批准才能查看我的消息(1表示上锁，0表示解锁)')
    parser.add_argument('-m', '--me', action='store_true', help='查看个人信息')
    parser.add_argument('-u', '--user', help='查看他人信息')
    parser.add_argument('-l', '--view', action='store_true', help='浏览模式')
    parser.add_argument('-d', '--random', action='store_true', help='随便看看')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    parser.add_argument('-V', '--version', action='store_true', help='显示版本号')
    return parser.parse_known_args()


def open_fanfou():
    import webbrowser
    webbrowser.open_new_tab('http://fanfou.com')


def handler(signal, frame):
    print('\nBye!')
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, handler)

    fan = Fan()
    args, unknown = parse_args()

    level = logging.DEBUG if args.verbose >= 2 else logging.INFO
    logging.basicConfig(level=level,
                        format='%(asctime)s [%(module)14s] [line:%(lineno)4d] [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    if args.save_all_statuses:
        fan.save_all_statuses(args.save_all_statuses)
    elif args.revert:
        fan.revert()
    elif args.protect is not None:
        fan.api.protect(bool(args.protect))
    elif args.me:
        fan.me()
    elif args.user:
        s, user = fan.api.users_show(id=args.user)
        if s:
            fan.display_user(user)
    elif args.view:
        fan.view()
    elif args.random:
        fan.random_view()
    elif args.version:
        import fanfoucli
        print(fanfoucli.__version__)
    else:
        status = ''
        unknown_str = ''
        if unknown:
            unknown_str = ''.join(unknown).strip()
        if unknown_str == '-':  # fan - read status from stdin
            status = sys.stdin.read()
        elif args.new:  # fan -n something
            status = ' '.join(args.new)
        elif not sys.stdin.isatty() and not args.image:  # echo something | fan
            status = sys.stdin.read()
        elif unknown:  # fan anything
            status = ' '.join(unknown)
        elif not args.image:
            open_fanfou()
            return
        # 发图片
        if args.image:
            fan.upload_photos(status, args.image)
        else:
            fan.update_status(status)


if __name__ == '__main__':
    main()
