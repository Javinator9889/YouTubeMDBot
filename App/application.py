from argparse import ArgumentParser, Namespace


def main(arguments: Namespace):
    from os import path
    token = arguments.token
    youtube_api_key = arguments.youtube
    creator_id = arguments.creator
    must_show_version = arguments.version
    if must_show_version:
        print("Version")
        exit(0)
    if not path.exists("app_data.dict"):
        if not token:
            ValueError("You must add token at least the first time you execute this app")
        elif not youtube_api_key:
            ValueError("You must include the YouTube API Key at least the first time you execute this app")
        elif not creator_id:
            ValueError("You must include the creator ID (Telegram) at least the first time you execute this app")
        else:
            with open("app_data.dict", "wb") as app_data_file:
                import pickle
                app_data = {"TOKEN": token,
                            "YT_API": youtube_api_key,
                            "CREATOR_ID": creator_id}
                pickle.dump(app_data, app_data_file, pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    args = ArgumentParser()
    args.add_argument("-t",
                      "--token",
                      help="Telegram token obtained via BotFather",
                      type=str)
    args.add_argument("-y",
                      "--youtube",
                      help="YouTube API Key",
                      type=str)
    args.add_argument("-c",
                      "--creator",
                      help="Telegram ID of the creator",
                      type=int)
    args.add_argument("-v",
                      "--version",
                      help="Application version",
                      action="store_true")
    main(args.parse_args())
