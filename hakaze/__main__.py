import sys
import argparse
import uvicorn
import hakaze

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="hakaze command line")
    parser.add_argument("-s", "--serve", action="store_true", dest="serve")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", default="8000")

    parser.add_argument("--fix-db-array", action="store_true")
    parser.add_argument("--work", action="store_true")

    parser.add_argument("--run")

    args = parser.parse_args()
    if args.serve:
        uvicorn.run(create_app(), host=args.host, port=args.port)
    elif args.fix_db_array:
        hakaze.database.pages_object_to_array()
    elif args.work:
        hakaze.exhentai.process_queued_jobs(False)
    elif args.run:
        pass
        #print(sys.modules.keys())
        #fn = getattr(sys.modules['hakaze.database'], args.run)
        #fn()
