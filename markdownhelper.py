import os


def write_markdown(comic_settings):
    filename = str(comic_settings['page']).rjust(3, '0') + ".mdx"
    output_file = os.path.join(comic_settings['gatsby_dir'], filename)
    print('writing ' + output_file)
    output = [
              '---\n',
              'chapter: ' + str(comic_settings['chapter']) + '\n',
              'page: ' + str(comic_settings['page']) + '\n',
              'posted: ' + comic_settings['posted_date'] + '\n',
              'comic: ' + './' + os.path.basename(comic_settings['comic_file']) + '\n',
              'type: comic\n'
              '---\n',
              '\n',
              comic_settings['note'] + '\n'
              ]

    md_file = open(output_file, 'w')
    md_file.writelines(output)
    md_file.close()
