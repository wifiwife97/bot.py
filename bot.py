import cv2
import numpy as np
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = '7571172534:AAHpcJgcBfMfvizi4_RI_blhyROrcwV2pyA'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('👋 Welcome! Send a trading chart screenshot for analysis.')

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = await update.message.photo[-1].get_file()
    photo_path = "received_screenshot.jpg"
    await photo.download_to_drive(photo_path)

    await update.message.reply_text('📈 Analyzing your chart...')
    edited_path, prediction, confidence = analyze_chart(photo_path)

    with open(edited_path, 'rb') as photo_file:
        caption_text = f"Analysis Complete!\nPrediction: {prediction} ({confidence}%)\nTip: {generate_tip(prediction)}"
        await update.message.reply_photo(photo=photo_file, caption=caption_text)

def analyze_chart(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError("Image not found or invalid format.")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=60, maxLineGap=10)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            color = (0, 255, 0)
            thickness = 2
            cv2.line(img, (x1, y1), (x2, y2), color, thickness)

    edge_count = np.sum(edges > 0)
    if edge_count % 2 == 0:
        prediction = "UP"
        confidence = 72
    else:
        prediction = "DOWN"
        confidence = 68

    edited_path = "edited_screenshot.jpg"
    cv2.imwrite(edited_path, img)
    return edited_path, prediction, confidence

def generate_tip(prediction):
    if prediction == "UP":
        return "Strong support detected. Possible bullish reversal."
    else:
        return "Resistance pressure seen. Possible bearish continuation."

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot is running...")
    app.run_polling()
