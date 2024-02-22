from PIL import Image, ExifTags
import PIL

import pathlib



project_dir = pathlib.Path('__file__').resolve().parents[2]
print(project_dir)


def basic_pil_test(img_path: str | pathlib.Path):
    img: PIL.Image = Image.open(img_path)
    print(f"Image loaded from: {img_path}")
    print(f"Image format: {img.format}")
    print(f"Image size: {img.size}")
    print(f"Image mode: {img.mode}")
    # print(f"Image info: {img.info}")
    print(f"Image exif:")
    exif = img._getexif()
    for tag, value in exif.items():
        tag_name = ExifTags.TAGS.get(tag, tag)
        value_str = str(value)
        if len(value_str) > 60:
            value_str = value_str[:60] + '**snip**'

        print(f'    {tag_name}: {value_str}')

    print()


if __name__ == '__main__':
    img_iphone = project_dir / 'pic' / 'example1.jpg'
    basic_pil_test(img_iphone)

    img_nikon = project_dir / 'pic' / 'example2.jpg'
    basic_pil_test(img_nikon)
