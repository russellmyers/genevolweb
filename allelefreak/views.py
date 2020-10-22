from django.shortcuts import render
import plotly.graph_objs as go
import plotly
from getools.popdist import PopDist
from .forms import AlleleFreakForm

import logging
logger = logging.getLogger(__name__)

# Create your views here.

def build_data(form):
    init_freq_a = form.cleaned_data['init_freq_a']
    pop_size = form.cleaned_data['pop_size']
    if pop_size == -1:
        pop_size = None
    fitnesses = [form.cleaned_data['fitness_AA'], form.cleaned_data['fitness_Aa'], form.cleaned_data['fitness_aa']]
    inbreeding_coefficient = form.cleaned_data['inbreeding_coefficient']
    num_gens = form.cleaned_data['num_gens']

    pd = PopDist(init_freq_a, genotype_fitnesses=fitnesses, pop=pop_size, F=inbreeding_coefficient, verbose=0)
    pd.sim_generations(num_gens)

    # x_data = [i for i in range(len(pd.gens))]
    # y_data = [round(gen.out_fa,3) for gen in pd.gens]
    #
    # return {'x_data': x_data,'y_data': y_data}
    return pd



def plot_graph_as_div(data_in, show_allele = 1):

    if show_allele == 1:
        line_type = 'solid'
    else:
        #line_type = 'dash'
        line_type = 'solid' #changed mind. Show both as solid

    data_list = []
    marker_colors = ['green','blue','orange','yellow','red','black','purple']
    for i,data in enumerate(data_in):
        data_list.append(go.Scatter(x=data['x_data'],y=data['y_data'],mode='lines',line={'dash': line_type, 'color': marker_colors[i % len(marker_colors)]}, name='run: ' + str(i+1),
                                    opacity=0.8))#,marker_color=marker_colors[i % len(marker_colors)]))

    if len(data_in) == 0:
        data_list.append(go.Scatter(x=[], y=[], mode='lines',
                                line={'dash': line_type, 'color': marker_colors[0 % len(marker_colors)]},
                                name='run: ' + str(0),
                                opacity=0.8))  # ,marker_color=marker_colors[i % len(marker_colors)]))

    allele_text = "a" if show_allele == 1 else "A"

    if len(data_in) == 0:
        x_limit = 400
    else:
        x_limit = data_in[0]['x_data'][-1]


    plot_div = plotly.offline.plot({"data": data_list,
                                    "layout": go.Layout(xaxis_title="Generations",
                                                        yaxis_title="Allele <b>" + allele_text + "</b> Frequency",
                                                        title="Allele '<b>" + allele_text + "'</b> - Frequencies over Generations",
                                                        yaxis=dict(
                                                            range=[0, 1]),
                                                        xaxis=dict( range=[0,x_limit]),
                                                        plot_bgcolor="rgb(240,240,240)")},
                                   output_type='div')

    return plot_div

def show_graph(request,form,add_new_plot_from_form=False, show_allele=1, auto_clear=False):

    saved_pop_dists = request.session.get('saved_pop_dists', [])

    context = {}

    if len(saved_pop_dists) == 0 and (not add_new_plot_from_form):
       context['no_data'] = True

    plot_data = []
    for saved_pop_dist in saved_pop_dists:
        pd = PopDist.pop_dist_from_json(saved_pop_dist)
        plot_data.append(pd.get_plot_data(allele = show_allele))

    if add_new_plot_from_form:
        new_pd = build_data(form)
        data = new_pd.get_plot_data(show_allele)
        plot_data.append(data)
        saved_pop_dists.append(new_pd.to_json())
        request.session['saved_pop_dists'] = saved_pop_dists
        request.session.modified = True

    #plot_div = plot_graph_as_div(plot_data, show_allele)  old code to generate plot js code n python
    plot_div = ''  #<div>Hello</div>
    context['plot_div'] = plot_div
    context['form']  = form
    context['sel_allele'] = show_allele
    context['auto_clear'] = auto_clear
    context['plot_data'] = plot_data
    context['show_allele'] = show_allele

    return render(request, "allelefreak/allele_freak.html", context=context)



def allele_freak(request):
    logger.info('Allele Freak')

    default_allele_choice = 1 # little a
    show_allele_choice = default_allele_choice
    auto_clear_choice = False


    if request.method == 'POST':

        form = AlleleFreakForm(request.POST)
        if 'show_allele' in request.POST:
            print('aha - show allele')

            if form.is_valid():
                show_allele_choice = int(form.cleaned_data['show_allele']) - 1
                auto_clear_choice = form.cleaned_data['auto_clear']
                print('allele choice selected: ',show_allele_choice)
            else:
                print('form not valid')

        if 'clear' in request.POST:
            print('clear pressed')
            request.session['saved_pop_dists'] = []
            return show_graph(request, form, add_new_plot_from_form=False, show_allele = show_allele_choice, auto_clear = auto_clear_choice)
        elif auto_clear_choice:
            print('clearing')
            request.session['saved_pop_dists'] = []
            return show_graph(request, form, add_new_plot_from_form=True, show_allele = show_allele_choice, auto_clear = auto_clear_choice)
        elif 'submitform' in request.POST:
           if form.is_valid():
                return show_graph(request,form,add_new_plot_from_form=True, show_allele = show_allele_choice, auto_clear = auto_clear_choice)
        else:
            return show_graph(request, form, add_new_plot_from_form=False, show_allele = show_allele_choice, auto_clear = auto_clear_choice)
    else:
        form = AlleleFreakForm(initial={'show_allele':str(show_allele_choice + 1)})

    return show_graph(request, form, add_new_plot_from_form=False, show_allele = show_allele_choice, auto_clear = auto_clear_choice)
    #return render(request, "common/allele_freak.html", {'form':form})
