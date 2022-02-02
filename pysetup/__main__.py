import sys, argparse
from os import path
from .model import Model

def main():
    parser = argparse.ArgumentParser(
        prog="Druid-config",
        description="Druid config generator")
    parser.add_argument("-x", "--vars", action="store_true",
                    help="print the variables (context)")
    parser.add_argument("-c", "--config", action="store_true",
                    help="print the computed configuration")
    parser.add_argument("-d", "--dry-run", action="store_true",
                    help="dry-run: load and verify, but don't generate")
    parser.add_argument("template", help='path to the the YAML template')
    args = parser.parse_args()
    #print(vars(args))

    root = args.template
    if not path.isfile(root):
        if not root.lower().endswith('.yaml'):
            root += '.yaml'
    if not path.isfile(root):
        print("Template {} does not exist.".format(args.template), file=sys.stderr)
        return

    model = Model(root)
    model.load()
    if args.vars:
        model.print_context()
    if args.config:
        model.print_config()
    if not args.dry_run:
       model.build()
    return 0

sys.exit(main())