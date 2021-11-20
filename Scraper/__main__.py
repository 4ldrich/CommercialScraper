import airbnb_scraper
import data_save
from getpass import getpass

### User inputs

print('________________________Airbnb Webscraper___________________________', end = '\n\n')

# User input for speed
speed_decision = input('Welcome. Do you have an internet speed of less than 2.5Mb/s and wish to enable slow mode?\n\
Warning: It is recommended that you only run a sample of the scraper in slow mode, as the full session could take >12 hours.\n\
[y/n]: ')

speed_flag = True if speed_decision.lower() == 'y' or speed_decision.lower() == 'yes' else False

if speed_flag:
    print('Scraping at slow speed', end = '\n\n')
else:
    print('Scraping at normal speed', end='\n\n')


# User input for sample
sample_decision = input('Do you wish to run the full scraper, and scrape all products from arbnb? Selecting \'n\' will lock the scraper to a sample\n\
[y/n]: ')

sample_flag = False if sample_decision.lower() == 'y' or sample_decision.lower() == 'yes' else True

if sample_flag:
    print('Scraping a sample', end = '\n\n')
else:
    print('Scraping all data. Please ensure your PC has its power saving settings OFF before proceeding, and it is recommended to leave your laptop plugged in if the battery is poor.', end='\n\n')



# User inputs for data storage
print('_________Data Storage Options_________', end = '\n\n')
print('Below are all the options to store the data from the webscraper. Please enter [y/n] for each data option:')
print('Note: Please ensure that all of your credentials are correct where applied, as well as that you have open connections to your databased/cloud locations. There will not be a chance to change credentials if you get them wrong.')
print('Note: All local data save options are stored in a created folder called data. Please ensure that there is no folder in the immediate directory already with that name, as this may cause issues.', end = '\n\n')

# Save csv
csv_desc = input('Save data to csv? [y/n]: ')
if csv_desc.lower() == 'y' or csv_desc.lower() == 'yes':
    csv_name = input('Please enter csv file name: ')
# Save JSON
json_desc = input('Save data to json? [y/n]: ')
if json_desc.lower() == 'y' or json_desc.lower() == 'yes':
    json_name = input('Please enter json file name: ')
# Save pkl
pickle_desc = input('Save data to pickle? [y/n]: ')
if pickle_desc.lower() == 'y' or pickle_desc.lower() == 'yes':
    pkl_name = input('Please enter pkl file name: ')
# Save Postgresql
postgres_desc = input('Save data to postgresql database? (requires an active connection) [y/n]: ')
if postgres_desc.lower() == 'y' or postgres_desc.lower() == 'yes':
    database_name = input('Please enter the database name that you wish to save in: ')
    table_name = input('Please enter the name of the table you wish to assign: ')
    username = input('Please enter the postgresql username: ')
    password = getpass('Please enter your postgresql password: ')
    hostname = input('Please input the postgresql hostname: ')
    port = input('Please enter the port no.: ')
    print()
# Save images locally
image_desc = input('Save images locally? [y/n]: ')
# Save data/images to s3
s3_data_desc = input('Save data to an AWS s3 bucket? [y/n]: ')
s3_img_desc = input('Save images to an AWS s3 bucket? [y/n]: ')
if s3_img_desc.lower() == 'y' or s3_img_desc.lower() == 'yes' \
    or s3_data_desc.lower() == 'y'or s3_data_desc.lower() == 'yes':
    bucket_name = input('Please enter the bucket name: ')
    access_key = input('Please enter your s3 buckets access key: ')
    secret_key = getpass('Please input the secret access key of your bucket: ')
    region_name = input('Please enter region name: ')
    if s3_img_desc.lower() == 'y' or s3_img_desc.lower() == 'yes':
        img_name = input('Please enter the IMAGE directory inside the s3 bucket you wish to assign: ')
    if s3_data_desc.lower() == 'y' or s3_data_desc.lower() == 'yes':
        df_name = input('Please enter the DATASET directory inside the s3 bucket you wish to assign: ')


### Executing Scraper
scraper = airbnb_scraper.Scraper(slow_internet_speed=speed_flag)
df, images = scraper.scrape_all(sample = sample_flag)

saver = data_save.Save(df, images)

### Executing Saver

# Save csv
if csv_desc.lower() == 'y' or csv_desc.lower() == 'yes':
    saver.df_to_csv(csv_name)

# Save JSON
if json_desc.lower() == 'y' or json_desc.lower() == 'yes':
    saver.df_to_json(json_name)

# Save pkl
if csv_desc.lower() == 'y' or csv_desc.lower() == 'yes':
    saver.df_to_pickle(pkl_name)

# Save SQL
if postgres_desc.lower() == 'y' or postgres_desc.lower() == 'yes':
    try:
        saver.df_to_postgresql(table_name, username, password, hostname, port, database_name)
    except Exception as e:
        print(e)

# Save df to s3
if s3_data_desc.lower() == 'y'or s3_data_desc.lower() == 'yes':
    try:
        saver.df_to_s3(access_key, region_name, secret_key, bucket_name, df_name)
    except Exception as e:
        print(e)
# Save images to s3
if s3_img_desc.lower() == 'y' or s3_img_desc.lower() == 'yes':
    try:
        saver.images_to_s3(access_key, region_name, secret_key, bucket_name, img_name)
    except Exception as e:
        print(e)


###############################################################
# TO DO LIST:
    # write requirements.txt
    # containerise in a docker file
    # test it!
