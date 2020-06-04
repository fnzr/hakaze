import os
import sys
import argparse
import uvicorn
import hakaze


def backup_db():
    import subprocess
    from datetime import datetime
    try:
        subprocess.run(
            "docker-compose", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        print(
            "docker-compose command not found. The --backup command should be executed from the host."
        )
    uri = os.getenv("MONGO_URI")
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    subprocess.run(["docker-compose", "exec", "mongo", "mongodump", f"--uri={uri}", f"--archive=/backup/{now}.dump"])

def restore_db(filename, dry):
    import subprocess
    try:
        subprocess.run(
            "docker-compose", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        print(
            "docker-compose command not found. The --restore command should be executed from the host."
        )
    fullpath = f"/backup/{filename}"
    if not os.path.isfile(fullpath):
        raise FileNotFoundError("Provided file {} does not exist.", fullpath)
    uri = os.getenv("MONGO_URI")
    args = ["docker-compose", "exec", "mongo", "mongorestore", f"--uri={uri}", f"--archive={fullpath}"]
    if dry:
        args.append("--dryRun")
    subprocess.run(args)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="hakaze command line")
    parser.add_argument("-s", "--serve", action="store_true", dest="serve")

    parser.add_argument("--fix-db-array", action="store_true")

    parser.add_argument("--run", nargs="+")

    parser.add_argument("-d", "--download")

    parser.add_argument("-n", "--ndownload")

    parser.add_argument("-p", "--npage")

    parser.add_argument("--backup", action="store_true")

    parser.add_argument("--restore")

    parser.add_argument("--dry", action="store_true")

    args = parser.parse_args()
    if args.serve:
        print("uvicorn hakaze.server:app --host 0.0.0.0 --port 8080 --reload")
    elif args.download:
        from hakaze import exhentai
        exhentai.save_gallery(args.download)
    elif args.ndownload:
        from hakaze import nhentai
        page = int(args.npage) if args.npage else 1
        nhentai.save_gallery(args.ndownload, page)
    elif args.backup:
        backup_db()
    elif args.restore:
        restore_db(args.restore, args.dry)
    elif args.run:
        import importlib

        module = f"hakaze.{args.run[0]}"
        importlib.import_module(module)
        fn = getattr(sys.modules[module], args.run[1])
        fn()
