from django.shortcuts import render
# from getools.popdist import PopDist
from getools.popdist import PopDist
import plotly.graph_objs as go
import plotly
# from .forms import AlleleFreakForm


def plot_test(request):

    # if request.method == 'POST':
    #     # create a form instance and populate it with data from the request:
    #     form = AlleleFreakForm(request.POST)
    #     # check whether it's valid:
    #     if form.is_valid():
    #         # process the data in form.cleaned_data as required
    #         # ...
    #         # redirect to a new URL:
    #         return show_graph(request,form)
    #
    #
    #     # if a GET (or any other method) we'll create a blank form
    # else:
    #     form = AlleleFreakForm()
    #
    # return render(request, "common/plot_test.html", {'form':form})

    # import plotly.express as px
    # labels = ['Oxygen', 'Hydrogen', 'Carbon_Dioxide', 'Nitrogen']
    # values = [4500, 2500, 1053, 500]

    num_gens = request.GET.get('num_gens')
    if num_gens is None:
        num_gens = 10
    else:
        num_gens = int(num_gens)
    fa = request.GET.get('fa')
    if fa is None:
        fa = 0.5
    else:
        fa = float(fa)
    fitnesses = request.GET.get('fit')
    if fitnesses is None:
        fitnesses = [1.0, 1.0, 1.0]
    else:
        fitnesses = [float(fit) for fit in fitnesses.split(',')]

    pop = request.GET.get('pop')
    if pop is None:
        pass
    else:
        pop = int(pop)

    pd = PopDist(fa, genotype_fitnesses=fitnesses, pop=pop, verbose=0)
    pd.sim_generations(num_gens)

    pd2 = PopDist(0.2, [0.9, 1.0, 1.0], pop=pop)
    pd2.sim_generations(num_gens)
    j_out = pd2.to_json()

    pd3 = PopDist.pop_dist_from_json(j_out)
    # pd3.gens[0].out_fa = 0.45
    # pd3.gens[1].out_fa = 0.45
    # pd3.gens[2].out_fa = 0.45

    pd1_copy = PopDist.pop_dist_from_json(pd.to_json())
    print('pd len: ', len(pd.gens))
    print('pd copy: ', len(pd1_copy.gens))

    # trace = plotly.offline.plot([plotly.graph_objs.Pie(labels=labels, values=values)],output_type='div')
    # return render(request, "common/plot_test.html", context={'plot_div': trace})

    x_data = [i for i in range(len(pd.gens))]
    y_data = [gen.out_fa for gen in pd.gens]

    x2_data = [i for i in range(len(pd2.gens))]
    y2_data = [gen.out_fa for gen in pd2.gens]

    x3_data = [i for i in range(len(pd3.gens))]
    y3_data = [gen.out_fa for gen in pd3.gens]

    # np.random.seed(42)
    # n = 1000
    # p = 0.5
    # nums = []
    # for i in range(0, 10000):
    #     nums.append(np.random.multinomial(n,[0.25,0.5,0.25]))
    #
    # firsts = [num[2] for num in nums]
    #
    # freqs = [[n / 1000.0 for n in num] for num in nums]

    # print(nums[:10])
    #
    # print (freqs[:10])

    plot_div = plotly.offline.plot({"data": [go.Scatter(x=x_data, y=y_data,
                                    mode='lines', name='test',
                                    opacity=0.8, marker_color='green'), plotly.graph_objs.Scatter(x=x2_data, y=y2_data,
                                    mode='lines', name='test2',
                                    opacity=0.8, marker_color='blue'),
                                    go.Scatter(x=x3_data, y=y3_data,
                                               mode='lines', name='test',
                                               opacity=0.8, marker_color='yellow')
                                    ],
                                    "layout": go.Layout(title="Allele Freak", xaxis_title="Generations",
                                                        yaxis_title="Allele a Frequency")},
                                    output_type='div')

    # plot_div = plotly.offline.plot([plotly.graph_objs.Histogram(x=firsts)],output_type='div')

    return render(request, "common/plot_test.html", context={'plot_div': plot_div})
