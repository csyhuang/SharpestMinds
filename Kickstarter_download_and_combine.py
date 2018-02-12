import pandas as pd
import numpy as np
import json
import datetime
import glob
import os
import re
import zipfile
import urllib.request

# Columns useful for training
cols_needed = ['id', 'name', 'blurb', 'main_category', 'category_name',
               'category_slug', 'creator_id', 'creator_name', 'country',
               'converted_pledged_amount', 'goal', 'created_at',
               'launched_at', 'deadline', 'state', 'state_changed_at',
               'spotlight', 'staff_pick', 'location_localized_name',
               'location_state', 'location_type']


def clean_csv(filepath, csv_file):
    """Take in the directory path and csv filename.
    Clean and save the processed csv filename with suffix '_cleaned.csv'."""

    fpath = filepath + csv_file
    print('Start cleaning ' + csv_file + '.')

    df = pd.read_csv(fpath)

    # Convert data to the right format
    df['created_at'] = df['created_at'].\
        apply(lambda x: datetime.datetime.
              fromtimestamp(int(x)).strftime('%Y-%m-%d %H:%M:%S'))

    df['launched_at'] = df['launched_at'].\
        apply(lambda x: datetime.datetime.
              fromtimestamp(int(x)).strftime('%Y-%m-%d %H:%M:%S'))

    df['deadline'] = df['deadline'].\
        apply(lambda x: datetime.datetime.
              fromtimestamp(int(x)).strftime('%Y-%m-%d %H:%M:%S'))

    df['state_changed_at'] = df['state_changed_at'].\
        apply(lambda x: datetime.datetime.
              fromtimestamp(int(x)).strftime('%Y-%m-%d %H:%M:%S'))

    df['category_slug'] = df['category'].apply(lambda x: json.loads(x)['slug'])
    df['category_name'] = df['category'].apply(lambda x: json.loads(x)['name'])
    df['main_category'] = df['category_slug'].\
        apply(lambda x: x.split('/')[0] if '/' in x else x)
    df['creator_id'] = df['creator'].apply(lambda x: json.loads(x)['id'])
    df['creator_name'] = df['creator'].apply(lambda x: json.loads(x)['name'])

    if 'localized_name' in df['location']:
        df['location_localized_name'] = \
            df['location'].apply(lambda x: json.loads(x)['localized_name']
                                 if isinstance(x, str) else np.nan)
    else:
        df['location_localized_name'] = \
            df['location'].apply(lambda x: json.loads(x)['name']
                                 if isinstance(x, str) else np.nan)

    df['location_state'] = \
        df['location'].apply(lambda x: json.loads(x)['state']
                             if isinstance(x, str) else np.nan)

    df['location_type'] = \
        df['location'].apply(lambda x: json.loads(x)['type']
                             if isinstance(x, str) else np.nan)
    # Convert True/False into 1/0
    df['spotlight'] = df['spotlight'].apply(lambda x: 1 if x else 0)

    df['staff_pick'] = df['staff_pick'].apply(lambda x: 1 if x else 0)

    # Deal with different column names
    if (('converted_pledged_amount' not in df.columns.tolist()) &
            ('usd_pledged' in df.columns.tolist())):
        df.rename({'usd_pledged': 'converted_pledged_amount'},
                  axis='columns', inplace=True)

    csv_save = fpath.rstrip('.csv') + '_cleaned.csv'
    df[cols_needed].to_csv(csv_save)
    print('Finish outputing ' + csv_save + '.')
    return None


def parse_csv_url(url="https://webrobots.io/kickstarter-datasets/"):
    """Parse the url of the .csv files from the html of the webrobots page"""

    opener = urllib.request.FancyURLopener({})
    f = opener.open(url)
    content = f.readlines()
    url_list, scrap_date = list(), list()

    for line in content:
        xx = re.match(r"<li>(..........)\W(.*)\[<a href=\"(.*).zip\">CSV</a>\]</li>",line.decode('utf-8'))
        if xx is not None:
            scrap_date.append(xx.group(1))
            url_list.append(xx.group(3) + '.zip')

    return scrap_date, url_list


def download_and_clean(scrap_date, url_list, semi_combined_dir):
    """Take in the scrap_date and url_list output from parse_csv_url,
    produce cleaned files in the same data directory using clean_csv
    and then combine them into a file with suffix all.csv in the specified
    directory semi_combined_dir"""

    cleaned_csv_list = list()
    for url, date_scrapped in zip(url_list, scrap_date):
        zipfile_name = "Kickstarter_" + date_scrapped + ".zip"
        if not os.path.exists(zipfile_name):
            print('Started downloading ' + zipfile_name)

            urllib.request.urlretrieve(url, zipfile_name)
        else:
            print(zipfile_name + ' exists.')
        print('Completed downloading ' + zipfile_name + ' exists.')

        zip_ref = zipfile.ZipFile(zipfile_name, 'r')
        zip_ref.extractall("Kickstarter_" + date_scrapped)
        zip_ref.close()

        file_path = "Kickstarter_" + date_scrapped + "/"

        csv_filelist = [file for file in glob.glob(file_path + "*.csv")]

        # This is to exclude processed files if the script was terminated.
        csv_filelist = [x for x in csv_filelist
                        if (('_cleaned' not in x) and ('_all' not in x))]

        # apply the cleaning function
        for x in csv_filelist:
            clean_csv('', x)

        # get all cleaned files
        all_csvFiles = glob.glob(file_path + "*cleaned.csv")

        # concatenate cleaned files
        frame = pd.DataFrame()
        list_ = []
        for file_ in all_csvFiles:
            df = pd.read_csv(file_, index_col=None, header=0)
            list_.append(df)
        frame = pd.concat(list_)
        frame.to_csv(semi_combined_dir + '/' + date_scrapped + "_all.csv")
        cleaned_csv_list.append(semi_combined_dir + '/' +
                                date_scrapped + "_all.csv")

        # Remove the files with suffix '_cleaned.csv'
        for item in all_csvFiles:
            os.remove(item)

    return cleaned_csv_list


def set_df_format(concerned_df):
    # Specify date format of several columns
    concerned_df.created_at = pd.to_datetime(concerned_df.created_at)
    concerned_df.launched_at = pd.to_datetime(concerned_df.launched_at)
    concerned_df.deadline = pd.to_datetime(concerned_df.deadline)
    concerned_df.state_changed_at = pd.to_datetime(concerned_df.
                                                   state_changed_at)
    # only filter out successful/failed cases
    concerned_df = concerned_df[concerned_df['state'].
                                isin(['successful', 'failed'])]
    concerned_df['state'] = concerned_df['state'].\
        apply(lambda x: 1 if x == 'successful' else 0)
    return concerned_df


def concatenate_semi_combined(cleaned_csv_list):
    """Change the known datetime columns to datetime format in a dataframe."""
    first_df = pd.read_csv(cleaned_csv_list[0])

    for filepaths in cleaned_csv_list[1:]:
        df = pd.read_csv(filepaths)
        first_df = pd.concat((first_df,
                              df[~df['name'].isin(first_df['name'])]), axis=0)
    first_df.to_csv(final_combined_filename)
    print('Output file: ' + final_combined_filename)


if __name__ == "__main__":

    # Set parameters:
    semi_combined_dir = 'semi_combined'
    final_combined_filename = 'combined_data.csv'
    num_of_files_to_include = 0  # 0: all; >0: number of files to scrap
    webrobots_url = "https://webrobots.io/kickstarter-datasets/"

    # Get the list of url and the date scraped from the html file
    # on https://webrobots.io/kickstarter-datasets/
    scrap_date, url_list = parse_csv_url(webrobots_url)

    # Download and clean the file, and put them into the newly opened directory
    if not os.path.exists(semi_combined_dir):
        os.makedirs(semi_combined_dir)
    if num_of_files_to_include == 0:
        num_of_files_to_include = len(scrap_date)

    cleaned_csv_list = download_and_clean(scrap_date[:num_of_files_to_include],
                                          url_list[:num_of_files_to_include],
                                          semi_combined_dir)

    # Final combination of all the semi-combined files
    concatenate_semi_combined(cleaned_csv_list)
    print('Finished preparing data.')







