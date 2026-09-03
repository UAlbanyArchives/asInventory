import argparse

from asDownload import run_download
from asUpload import run_upload
from asValidate import run_validate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='asinventory')
    subparsers = parser.add_subparsers(dest='command', required=True)

    def add_shared_paths(command_parser: argparse.ArgumentParser) -> None:
        command_parser.add_argument('--base-dir', help='Base directory for default input/output/complete/dao paths.')
        command_parser.add_argument('--input', dest='input_path', help='Override the input folder path.')
        command_parser.add_argument('--output', dest='output_path', help='Override the output folder path.')
        command_parser.add_argument('--complete', dest='complete_path', help='Override the complete folder path.')
        command_parser.add_argument('--dao', dest='dao_path', help='Override the dao folder path.')

    upload_parser = subparsers.add_parser('upload', help='Upload spreadsheet inventories to ArchivesSpace.')
    add_shared_paths(upload_parser)
    upload_parser.set_defaults(handler=run_upload)

    download_parser = subparsers.add_parser('download', help='Download an inventory spreadsheet from ArchivesSpace.')
    add_shared_paths(download_parser)
    download_parser.set_defaults(handler=run_download)

    validate_parser = subparsers.add_parser('validate', help='Validate spreadsheet dates and DAO references.')
    add_shared_paths(validate_parser)
    validate_parser.set_defaults(handler=run_validate)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.handler(
        base_dir=args.base_dir,
        input_path=args.input_path,
        output_path=args.output_path,
        complete_path=args.complete_path,
        dao_path=args.dao_path,
        interactive=False,
    )


if __name__ == '__main__':
    raise SystemExit(main())