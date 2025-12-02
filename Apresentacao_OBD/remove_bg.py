from PIL import Image
import sys

def remove_white_background(input_path, output_path):
    img = Image.open(input_path)
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        # Change all white (also shades of whites)
        # to transparent
        if item[0] > 200 and item[1] > 200 and item[2] > 200:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    img.save(output_path, "PNG")
    print("Successfully saved transparent image to", output_path)

if __name__ == "__main__":
    input_file = "/Users/mac2/.gemini/antigravity/brain/59aba3b6-c807-4b2a-a70b-d068fbc665fe/uploaded_image_1764559563061.jpg"
    output_file = "/Users/mac2/Documents/Backup Pen Drive - Janeiro 2025/Coisa Minha/DARDO/OBD/Projeto Site OBD/Apresentacao_OBD/assets/logo_main_transparent.png"
    remove_white_background(input_file, output_file)
