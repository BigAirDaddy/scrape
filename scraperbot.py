import discord
import time
from discord.ext import commands, tasks
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Create a new instance of intents
intents = discord.Intents.default()
intents.typing = False  # You can adjust these intents as needed

# Initialize the Discord bot with intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize the last_post_url variable
last_post_url = None

# Function to click the "Reply" button, scrape replies, and return
def click_reply_and_scrape_replies(driver):
    # Find and click the "Reply" button
    try:
        reply_button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div#reply-button-end ytd-button-renderer a'))
        )
        reply_button.click()
    except Exception as e:
        print(f"Error clicking the reply button: {str(e)}")

    # Wait for the replies to load (adjust the wait time as needed)
    time.sleep(10)  # Adjust as needed

    # Extract and save replies
    replies = driver.find_elements(By.CSS_SELECTOR, 'ytd-backstage-comment')
    reply_text = ""
    for reply in replies:
        reply_text += reply.find_element(By.CSS_SELECTOR, 'div#content').text + '\n'

    # Go back to the community post
    driver.back()

    return reply_text

# Function to scrape community posts and read replies
async def scrape_community_post_and_replies(ctx, channel_id, bot_token):
    global last_post_url

    # Initialize the Selenium WebDriver (use Chrome or Firefox WebDriver)
    driver = webdriver.Chrome()  # Use Chrome WebDriver
    # driver = webdriver.Firefox()  # Use Firefox WebDriver

    # Open the channel's community page
    channel_url = 'https://www.youtube.com/@DanielLarson-ob2jw/community'  # Replace with the actual channel URL
    driver.get(channel_url)

    # Find and extract the first community post (with explicit wait)
    try:
        first_post = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, 'ytd-backstage-post-thread-renderer'))
        )
    except Exception as e:
        print(f"No community posts found: {str(e)}")
        driver.quit()
        return

    # Extract the URL of the first post
    post_url = first_post.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')

    # Check if it's a new post
    if post_url != last_post_url:
        # Save the URL of the new post
        last_post_url = post_url

        # Extract and save the content of the first post
        post_content = first_post.find_element(By.CSS_SELECTOR, 'div#content').text

        # Extract and save replies for the first post if available
        reply_text = click_reply_and_scrape_replies(driver)

        # Send the post content and replies to Discord
        await ctx.send(f"**Post Content:**\n{post_content}\n\n**Replies:**\n{reply_text}")

    # Close the WebDriver
    driver.quit()

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    await scrape_task.start()

# Create a scheduled task to scrape periodically
@tasks.loop(minutes=4)  # Adjust the interval as needed
async def scrape_task():
    # Ask for user input: Discord channel ID and bot token
    channel_id = input("Enter your Discord channel ID: ")
    bot_token = input("Enter your bot token: ")

    # Get the channel where you want to send updates
    channel = bot.get_channel(int(channel_id))  # Convert the channel ID to an integer

    # Call the scraping function
    await scrape_community_post_and_replies(channel, channel_id, bot_token)

# Run the bot
bot.run(input("Enter your bot token: "))  # Ask for the bot token when running the script
