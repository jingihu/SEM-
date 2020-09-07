import os
import mimetypes

from django.shortcuts import render, HttpResponse
from django.http import FileResponse
from django.conf import settings
import xlrd

from app.models import Speech
import json

# Create your views here.


# def Partciple(request,all_speech,remain_speech,handle_speech,match_rule):
def Partciple(request,):

    if request.method == 'GET':
        cols_data=[]
        # obj_list = Speech.objects.all().values('all_word')
        #
        # for i  in obj_list:
        #     cols_data.append(i['all_word'])
        number =0

        return render(request,'part.html',{'word_list':cols_data,'len_word':number})
    context = {'status': True, 'msg': '导入成功'}

    try:
        customer_excel = request.FILES.get('excelFile')
        print(customer_excel)
        """
           打开上传的Excel文件，并读取内容
           注：打开本地文件时，可以使用：workbook = xlrd.open_workbook(filename='本地文件路径.xlsx')
        
        """

        workbook = xlrd.open_workbook(file_contents=customer_excel.file.read())

        table = workbook.sheet_by_index(0)
        print(table)
        table_ncols = table.ncols
        print(table_ncols)

        cols_data = list(set(table.col_values(1)))
        # print(cols_data)
        number = len(cols_data)
        if number != 0:
            Speech.objects.all().delete()

        cols_data_list = []

        for word in cols_data:
            obj = Speech(all_word=word)

            cols_data_list.append(obj)

        Speech.objects.bulk_create(cols_data_list)

        return render(request, 'part.html',{'word_list':cols_data,'len_word':number})

    except Exception as e:
        context['status'] = False
        context['msg'] = '导入失败'

        return render(request,'part.html', context)




from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def input_rule(request):
    if request.method == 'POST':
        all_rule = request.POST.getlist('all_rule[]')
        all_word = []
        word_obj = Speech.objects.all().values('all_word')
        for i  in word_obj:
            all_word.append(i['all_word'])
        use_word = []
        left_word = []

        handle_speech = {}
        for rule in all_rule:
            handle_speech[rule] = []


        for word in all_word:
            for rule in all_rule:
                if '&' in rule:
                    rules = rule.split('&')
                    for ruless in rules:
                        if ruless in word and rule != '':
                            handle_speech[rule].append(word)
                            use_word.append(word)
                            break
                else:
                    if rule in word and rule != '':

                        handle_speech[rule].append(word)
                        use_word.append(word)
                        break

        left_word =list( set(all_word) - set(use_word ))
        left_len = len(left_word)


        all_data = {
        'handle_speech' : handle_speech,
        'left_len' : left_len,
        'left_word' :left_word,
        }



    return HttpResponse(json.dumps(all_data))



def customer_tpl(request):
    """
    下载批量导入Excel列表
    :param request:
    :return:
    """
    tpl_path = os.path.join(settings.BASE_DIR, 'web', 'files', '批量导入客户模板.xlsx')
    content_type = mimetypes.guess_type(tpl_path)[0]
    response = FileResponse(open(tpl_path, mode='rb'), content_type=content_type)
    response['Content-Disposition'] = "attachment;filename=%s" % 'customer_excel_tpl.xlsx'
    return response