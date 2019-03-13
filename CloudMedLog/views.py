from django.shortcuts import render
from django.http.response import *
import os
import time
from cloudmed.settings import BASE_DIR, MEDIA_ROOT, UPLOAD_ROOT
from django import forms
from so.tcm import TcmPro

tcmPro = TcmPro()


def upload_image(req):

    if req.method == 'POST':
        print(req)
        my_file = req.FILES.get("file", None)
        type = req.POST.get("type", "face")
        if not my_file:
            print("no file to upload")
            return HttpResponse("")

        file_ext = os.path.splitext(my_file.name)[1]
        filename = str(time.time())+file_ext

        with open(os.path.join(UPLOAD_ROOT, filename), "wb") as f:
            for t in my_file.chunks():
                f.write(t)

        if type == "face":
            result = tcmPro.facePro(os.path.join(UPLOAD_ROOT, filename))
        else:
            result = tcmPro.tongPro(os.path.join(UPLOAD_ROOT, filename))
        return JsonResponse(decode_result(result, type))



"""
面诊返回值：
    返回类型：int
	faceDetectRes->人脸检测结果:0->未检测出人脸，1->成功检测出人脸
	faceColor->面部颜色检测结果:0->面白，1->面黑，2->面红,3->面黄，4->面青，5->正常
	faceGloss->面部光泽检测结果:0->有光泽，1->少光泽，2->无光泽
	lipDetectRes->嘴唇检测结果:0->未检测出嘴唇，1->成功检测出嘴唇
	lipColor->嘴唇颜色检测结果:0->淡白，1->淡红，2->红,3->暗红，4->紫
	返回值编码格式：result = faceDetectRes*1 + faceColor*10 + faceGloss*100 + lipDetectRes*1000 + lipColor*10000

	例子：人脸检测成功并且嘴唇检测成功：31251
	                其中，faceDetectRes = 1；faceColor = 5；faceGloss = 2；lipDetectRes = 1；lipColor = 3；
		  人脸检测成功并且嘴唇检测失败：251
					其中，faceDetectRes = 1；faceColor = 5；faceGloss = 2；lipDetectRes = 0；(lipColor无具体值)
	      人脸检测失败，此时嘴唇一定检测失败：0
	                其中，faceDetectRes = 0；lipDetectRes = 0；(faceColor，faceGloss和lipColor无具体值)
	                
	                
/*舌诊返回值：
	返回类型：int
	tongueDetectRes->舌体检测结果:0->未检测出舌像，1->成功检测出舌像
	tongueCrack->舌裂纹检测结果:0->未检测到裂纹,1->成功检测到裂纹
	tongueFatThin->舌胖瘦检测结果:0->正常(瘦),1->胖舌
	tongueCoatThickness->舌苔厚薄检测结果:0->薄,1->厚
	tongueCoatColor->舌苔颜色检测结果:0->苔白，1->苔黄
	tongueNatureColor->舌质颜色检测结果:0->舌暗红，1->舌淡白，2->舌淡红，3->舌红，4->舌深红（舌紫）
	返回值编码格式：result = tongueDetectRes*1 + tongueCrack*10 + tongueFatThin*100 + tongueCoatThickness*1000 + tongueCoatColor*10000 + tongueNatureColor*100000

	例子：舌诊成功：310101
					其中，tongueDetectRes = 1；tongueCrack = 0；tongueFatThin = 1；tongueCoatThickness = 0；tongueCoatColor = 1；tongueNatureColor = 3；
		  舌诊失败：0
		            其中，tongueDetectRes = 0；(tongueCrack，tongueFatThin，tongueCoatThickness，tongueCoatColor和tongueNatureColor无具体值)
*/

"""


def decode_result(result, type="face"):
    result = int(result)
    keys = None
    d = dict()
    d["result"] = str(result)
    if type == "face":
        keys = ["faceDetectRes", "faceColor", "faceGloss", "lipDetectRes", "lipColor"]
    else:
        keys = ["tongueDetectRes", "tongueCrack", "tongueFatThin", "tongueCoatThickness", "tongueCoatColor", "tongueNatureColor"]

    for k in keys:
        d[k] = result%10
        result =int(result/ 10)
    return d
