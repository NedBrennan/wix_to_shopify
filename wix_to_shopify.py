
import csv
import math
import pprint

tagObject = {}
productDictionary = {}
firstVariantDict = {}
secondVariantDict = {}
shopifyHeader = ['Handle', 'Title', 'Body (HTML)', 'Vendor', 'Tags', 'Published', 'Option1 Name', 'Option1 Value', 'Option2 Name', 'Option2 Value', 'Option3 Name', 'Option3 Value', 'Variant SKU', 'Variant Grams', 'Variant Inventory Tracker', 'Variant Inventory Qty', 'Variant Inventory Policy', 'Variant Fulfillment Service', 'Variant Price', 'Variant Compare At Price', 'Variant Requires Shipping', 'Variant Taxable', 'Variant Barcode', 'Image Src', 'Image Position', 'Image Alt Text', 'Gift Card', 'SEO Title', 'SEO Description', 'Google Shopping / Google Product Category', 'Google Shopping / Gender', 'Google Shopping / Age Group', 'Google Shopping / MPN', 'Google Shopping / AdWords Grouping', 'Google Shopping / AdWords Labels', 'Google Shopping / Condition', 'Google Shopping / Custom Product', 'Google Shopping / Custom Label 0', 'Google Shopping / Custom Label 1', 'Google Shopping / Custom Label 2', 'Google Shopping / Custom Label 3', 'Google Shopping / Custom Label 4', 'Variant Image', 'Variant Weight Unit', 'Variant Tax Code', 'Cost per item', 'Status', 'Standard Product Type', 'Custom Product Type']


def format_additional_info(row) :
    title = '<div class="additional-info-title">' + row[33] + '</div>'
    body = '<div class="additional-info-body">' + row[34] +'</div>'
    section = '<div class="additional-info-section>"' + title + body + '</div>'

    return section

def build_description(row) :
    if (row[33] != '') :
        additonalInfo = format_additional_info(row)
    else :
        additonalInfo = ''

    mainDescription = '<div class="main-description">' + row[3] + '</div>'
    description = '<div class=full-description-container>' + mainDescription + additonalInfo +'</div>'

    return description

def get_first_option(row, handle) :
    if (row[15] != '') :
        option1Value = row[17].split(';')[0]
        firstVariantDict[handle] = option1Value
    else :
        option1Value = ''

    return option1Value

def get_second_option(row, handle) :
    option2Value = row[20].split(';')[0]
    secondVariantDict[handle] = option2Value

    return option2Value

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
        newTags = ','.join(tags)

    return newTags

def define_shopify_variant_row(handle, name, price, secondVariantName) :
    row = [''] * 50
    row[0] = handle
    row[7] = name
    row[9] = secondVariantName
    row[12] = handle + '-' + name.lower().replace(' ', '-')
    row[13] = 0
    row[16] = 'deny'
    row[17] = 'manual'
    row[18] = price
    row[20] = 'TRUE'
    row[21] = 'TRUE'
    row[43] = 'lb'

    return row

def define_shopify_row(handle, title, description, tags, option1Name, option1Value, option2Name, option2Value, weight, price) :
    row = [''] * 50
    row[0] = handle
    row[1] = title
    row[2] = description
    row[4] = tags
    row[5] = 'TRUE'
    row[6] = option1Name
    row[7] = option1Value
    row[8] = option2Name
    row[9] = option2Value
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

def write_variant_row(row, writer) :

    # handle
    handle = row[0]

    # price
    price = float(productDictionary[row[0]]) + float(row[9])
    
    # option 1 name
    name = row[17]

    # option 2 name
    secondVariantName = row[20]

    # create shopify row
    newRow = define_shopify_variant_row(handle, name, price, secondVariantName)
    
    writer.writerow(newRow)

def write_main_row(row, writer) :

    # handle
    handle = row[0]

    # title
    title = row[2]

    # description
    description = build_description(row)

    # weight
    weight = row[14]

    # price
    price = row[8]

    # tags
    tags = write_tags(row[5])

    # option 1 Value
    option1Value = get_first_option(row, handle)
    
    # option 2 value
    option2Value = get_second_option(row, handle)

    # set base price for product in dictionary
    productDictionary[handle] = price

    
    if row[18] != '' :
        secondVariantDict[row[0]] = row[20].split(';')

    newRow = define_shopify_row(handle, title, description, tags, row[15], option1Value, row[18], option2Value, weight, price)
    writer.writerow(newRow)

    write_photos(row[4], row[0], writer)

def wix_to_shopify(fileName, newFileName) :

    reader = get_reader(fileName)
    writer = get_writer(newFileName)
    firstRow = True

    for row in reader :

        wixHandle = row[0]
        title = row[2]
        option1value = row[17]
        option2value = row[20]
        rowType = row[1]

        if firstRow :
            writer.writerow(shopifyHeader)
            firstRow = False

        if (rowType == 'Product' and title.__contains__('CBD') == False) :
            write_main_row(row, writer)

        elif rowType == 'Variant' :
            if option2value != '' :

                if option1value == firstVariantDict[wixHandle] and option2value == secondVariantDict[wixHandle][0] : 
                    print('skip')

                else :
                    write_variant_row(row, writer)

            else :
                
                if option1value != firstVariantDict[wixHandle] :
                    write_variant_row(row, writer)

    # count = 1

    # parameterWriter = get_writer('parameterWriter.csv')

    # for tag in tagObject :
    #     if count == 1 :
    #         parameterWriter.writerow(['collection-name'])
    #     row = ['']
    #     row[0] = tag
    #     parameterWriter.writerow(row)
    #     count += 1



wix_to_shopify('./whole_dogz_raw_list.csv', 'whole_dogz_upload.csv')