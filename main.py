import os
import pathlib


def get_cd_info(path):
    """
    Search to the lowest directory and return the name of the CD, the name of the artist and its file path.
    Args:
        path ([str]): File path to search
    Yields:
        [Tuple[str]]: dir_path, artist, cd_name
    """
    for root, dirs, _ in os.walk(path):
        if not dirs:
            p = pathlib.Path(root)
            yield root, p.parent.name, p.name
        for dir in dirs:
            get_cd_info(f"{path}\\{dir}")


def main():
    for path, artist, name in get_cd_info(r"E:\Music\HiRes"):
        print(path, artist, name)


if __name__ == "__main__":
    main()
