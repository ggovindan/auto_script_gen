from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

import simplejson
import read_json
from .forms import JsonTestForm

import sys
import traceback
import subprocess

def index(request):

#def get_json_text(request):
#    print "Enter method get_json_text"
    if request.method == 'POST':
        print "request method is post"
        #form = JsonTestForm(request.POST)
        post_text = request.POST.get('the_post')
        if post_text != "":
            print "form is valid"
            #call the read_json.py and pass the json script in the appropriate format
            # capture the result of it in some way and then redirect it to the results page
            try:
                #data_string=form.cleaned_data['jsonText']
                data_string = post_text

                data = simplejson.loads(data_string)
                print "data=", data
                with open("temp/test7777777.json", "w") as outfile:
                    simplejson.dump(data, outfile)

                read_json.main("temp/test7777777.json", None)
                subprocess.call(['autopep8', '--in-place', '--aggressive', '--aggressive', 'temp/test7777777.py'])
                f = open("temp/test7777777.py", "r")
                response_data = {}
                response_data['result'] = "success"
                response_data['data'] = f.read()
                #form.cleaned_data['pythonScript'] = f.read()
                #print "cleanded_data=", form.cleaned_data['pythonScript']
                return HttpResponse(simplejson.dumps(response_data), content_type="application/json")
                #return render(request, "ellora/index.html", {"form": form})
                #return HttpResponse("{}".format(f.read()))
            except Exception as e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                print ''.join('! ' + line for line in lines)            
                mystr = ''.join('! ' + line for line in lines)
                #form.cleaned_data['pythonScript'] = mystr
                #print "cleanded_data=", form.cleaned_data['pythonScript']
                response_data = {}
                response_data['result'] = "failure"
                response_data['data'] = mystr
                return HttpResponse(simplejson.dumps(response_data), content_type="application/json")
                #return render(request, "ellora/index.html", {"form": form})
                #return HttpResponse("{}".format(mystr))
        else:
            print "form is not valid!!"
    else:
        print "request type was not POST"
        form = JsonTestForm()
        return render(request, 'ellora/index.html', {'form': form})
