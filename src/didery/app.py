import ioflo.app.run


def main():
    print("MAIN")
    """ Main entry point for ioserve CLI"""
    # from didery import __version__
    args = ioflo.app.run.parseArgs(version="0.0.1")  # inject  version here

    ioflo.app.run.run(  name=args.name,
                        period=float(args.period),
                        real=args.realtime,
                        retro=args.retrograde,
                        filepath=args.filename,
                        behaviors=args.behaviors,
                        mode=args.parsemode,
                        username=args.username,
                        password=args.password,
                        verbose=args.verbose,
                        consolepath=args.console,
                        statistics=args.statistics)

if __name__ == '__main__':
    main()
