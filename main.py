import time
import argparse
from AutoKudos import AutoKudos
import schedule


def run_auto_kudos():
    auto_kudos = AutoKudos('https://www.strava.com/login')
    auto_kudos.run()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Auto giving kudos')
    parser.add_argument('--run-once', action='store_true', help='只运行一次')

    args = parser.parse_args()

    # 命令行参数，--run-once表示只运行一次
    if args.run_once:
        print("Program run once")
        run_auto_kudos()
    else:
        # 设置定时任务，每半个小时执行一次
        print("Program run every 20 minutes")
        schedule.every(20).minutes.do(run_auto_kudos)
        while True:
            # 运行定时任务
            schedule.run_pending()
            time.sleep(1)