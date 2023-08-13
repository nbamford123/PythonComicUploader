import os


def write_markdown(comicsettings):
    filename = str(comicsettings['page']).rjust(3, '0') + ".mdx"
    outputfile = os.path.join(comicsettings['gatsbydir'], filename)
    print('writing ' + outputfile)
    output = [
              '---\n',
              'chapter: ' + str(comicsettings['chapter']) + '\n',
              'page: ' + str(comicsettings['page']) + '\n',
              'posted: ' + comicsettings['postdate'] + '\n',
              'comic: ' + './' + os.path.basename(comicsettings['comicfile']) + '\n',
              'type: comic\n'
              '---\n',
              '\n',
              comicsettings['note'] + '\n'
              ]

    mdFile = open(outputfile, 'w')
    mdFile.writelines(output)
    mdFile.close()
