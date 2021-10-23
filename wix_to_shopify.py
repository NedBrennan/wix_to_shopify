
import csv
import os
import math
import pprint
def fn():       # 1.Get file names from directory
    file_list=os.listdir('')
    return file_list

tagObject = {}
productDictionary = {}
firstVariant = {}

def format_additional_info(row) :
    title = '<div class="additional-info-title">' + row[33] + '</div>'
    body = '<div class="additional-info-body">' + row[34] +'</div>'
    section = '<div class="additional-info-section>"' + title + body + '</div>'

    return section

def get_reader(fileName) :
    f = open(fileName, 'r')
    reader = csv.reader(f)
    return reader

def get_writer(fileName) :
    w = open(fileName, 'w')
    # create the csv writer
    writer = csv.writer(w)
    return writer

def write_photos(photoArray, handle, csvWriter) :
    photoArray = photoArray.split(';')

    photoCount = 1
    for photo in photoArray :
        wixUrl = 'https://static.wixstatic.com/media/' + photo
        row = [''] * 50
        row[0] = handle
        row[23] = wixUrl
        row[24] = photoCount
        photoCount += 1
        csvWriter.writerow(row)

def write_tags(tagString) :
    tags = tagString.split(';')
    for tag in tags :
        tagObject[tag] = True
        tags = ','.join(tags)

    return tags

def write_main_row(row, writer) :

    #handle
    handle = row[0]

    #title
    title = row[2]

    #description
    if (row[33] != '') :
        additonalInfo = format_additional_info(row)
    else :
        additonalInfo = ''

    mainDescription = '<div class="main-description">' + row[3] + '</div>'
    description = '<div class=full-description-container>' + mainDescription + additonalInfo +'</div>'

    #weight
    weight = row[14]

    #price
    price = row[8]

    #tags
    tags = write_tags(row[5])

    if (row[15] != '') :
        option1Value = row[17].split(';')[0]
        firstVariant[handle] = option1Value
    else :
        option1Value = ''

    productDictionary[handle] = price

    newRow = define_shopify_row(handle, title, description, tags, row[15], option1Value, weight, price)
    writer.writerow(newRow)

    write_photos(row[4], row[0], writer)

def define_shopify_row(handle, title, description, tags, option1Name, option1Value, weight, price) :
    row = [''] * 50
    row[0] = handle
    row[1] = title
    row[2] = description
    row[4] = tags
    row[5] = 'TRUE'
    row[6] = option1Name
    row[7] = option1Value
    row[12] = handle + '-' + option1Value.lower().replace(' ', '-')
    row[13] = math.floor(float(weight) * 454)
    row[16] = 'deny'
    row[17] = 'manual'
    row[18] = price
    row[20] = 'TRUE'
    row[21] = 'TRUE'
    row[27] = title
    row[43] = 'lb'
    row[46] = 'active'

    return row

def define_shopify_variant_row(handle, name, price) :
    row = [''] * 50
    row[0] = handle
    row[7] = name
    row[12] = handle + '-' + name.lower().replace(' ', '-')
    row[13] = 0
    row[16] = 'deny'
    row[17] = 'manual'
    row[18] = price
    row[20] = 'TRUE'
    row[21] = 'TRUE'
    row[43] = 'lb'

    return row

def write_variant_row(row, writer) :

    # handle
    handle = row[0]

    # price
    
    price = float(productDictionary[row[0]]) + float(row[9])
    
    # option name
    name = row[17]

    newRow = define_shopify_variant_row(handle, name, price)
    writer.writerow(newRow)

def wix_to_shopify(fileName, newFileName) :

    reader = get_reader(fileName)
    shopify = get_reader('./shopify_template.csv')
    writer = get_writer(newFileName)

    shopifyCount = 1

    for row in shopify :
        if shopifyCount == 1 :
            writer.writerow(row)
            shopifyCount += 1

    for row in reader :
        if (row[1] == 'Product' and row[2].__contains__('CBD') == False) :
            write_main_row(row, writer)
        elif row[1] == 'Variant' and row[17] != firstVariant[row[0]] :
            write_variant_row(row, writer)

    # pprint.pprint(productDictionary)



wix_to_shopify('./whole_dogz_raw_list.csv', 'whole_dogz_upload.csv')