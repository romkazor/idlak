#takes output from cart lts and produces input for idlak
import treenode, sys, glob, os.path, argparse

def load_trees(indir, outfile, diags = None):
    treefiles = glob.glob(indir + '/*/tree.dat')
    treefiles.sort()
    if diags is None:
        fplog = open(os.devnull, 'w', encoding='utf8')
    else:
        fplog = open(diags, 'w', encoding='utf8')
    fp = open(outfile, 'w', encoding='utf8')

    fp.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
    fp.write("<lts>\n")
    for t in treefiles:
        ltrdir = os.path.basename(os.path.dirname(t))
        ltr = ltrdir.split('_')[0]
        if ltr=="stress":
            ltr="0"

        print ("Loading '{}' from {}".format(ltr, t))
        tree_tkns = treenode.tokenise_tree(t)
        tree_list = treenode.mklist(tree_tkns)
        tree, nodelist = treenode.parse(tree_list[0], [])
        fplog.write("Letter: {}\n".format(ltr))
        sorted_nodelist = treenode.prune_tree(tree, nodelist, fplog)
        terms, non_terms = treenode.reorder(sorted_nodelist)

        fp.write("\t<tree ltr='{}' rootnode='N{}' terminal='{}' nonterminal='{}'>\n".format(
            ltr, len(terms), len(terms), len(non_terms))
        )
        idx = 0
        for i in terms:
            fp.write("\t\t<node id='T{}' val='{}'/>\n".format(idx, i[0]))
            idx += 1
        for i in non_terms:
            fp.write("\t\t<node id='N{}' pos='{}' posval='{}' yes='{}' no='{}'/>\n".format(idx, i[0], i[1], i[2], i[3]))
            idx += 1
        fp.write("\t</tree>\n")
        fp.flush()
        fplog.flush()
    fp.write("</lts>\n")
    fp.close()
    fplog.close()

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--diagnostics')
parser.add_argument('wagondir')
parser.add_argument('outputxml')
args = parser.parse_args()
load_trees(args.wagondir, args.outputxml, diags = args.diagnostics)
