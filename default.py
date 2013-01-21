# -*- coding: utf-8 -*-

'''
 XBMC tv5monde plugin.
 This is the first trial of the tv5monde plugin for XBMC.
 This plugins gets the videos from tv5mondeplus web page and shows them ordered by category.
 This plugin depends on the lutil library functions.
 jamontes 2013.
'''

import lutil

pluginhandle = int(sys.argv[1])

# Entry point
def run():
    lutil.log("tv5monde.run!! handle = [" + str(pluginhandle) + "]")
    
    # Get params
    params = lutil.get_plugin_parms()
    
    if params.get("action") is None:
        index(params)
    else:
        action = params.get("action")
        exec action+"(params)"

# This function generate the video index ordered by category.
def index(params):
    lutil.log("tv5monde.index "+repr(params))

    url = 'http://www.tv5mondeplus.com/videos'
    buffer_html = lutil.carga_web(url)
    list_pattern = '<div id="tri-par-genre"(.+?)</ul>'
    lista_genre = lutil.find_first(buffer_html, list_pattern)
    genre_pattern = '<li><a id="([0-9]+)" [^>]+>([^<]+)<'

    for genre, label in lutil.find_multiple(lista_genre, genre_pattern):
        genre_url = 'http://www.tv5mondeplus.com/get/videos?pg=0&type=genre&sort=%s&loadpg=false&order=date' %  genre
        lutil.log('tv5monde.index url=["%s"] genre=["%s"]' % (genre_url, label))
        lutil.addDir(action="main_list", title=label, url=genre_url)

    lutil.close_dir(pluginhandle)


# This function generates the list of videos available on each category, ordered by date.
def main_list(params):
    lutil.log("tv5monde.main_list "+repr(params))

    # Loads the list of videos of the selected category based on the json object retrieved from the server.
    buffer_json = lutil.get_json(params.get("url"))
    pattern_videos = '<a title="([^"]+)" href="/video/([^/]+)/[^"]+"> <img src="([^"]+)" .*?<div class="bookmark" id="book_([0-9]+)">'
    videolist = lutil.find_multiple(buffer_json['content'], pattern_videos)

    for title, day, thumbnail, videoid in videolist:
        video_url = 'http://www.tv5mondeplus.com/video-xml/get/%s' % videoid
        title = title.replace('&quot;', '"')
        lutil.log('videolist: URL: "%s" Descripcion: "%s" Date: "%s" Thumbnail: "%s"' % (video_url, title, day, thumbnail))

        plot = title
        lutil.addLink(action="play_video", title='%s (%s)' % (title, day), plot=plot, url=video_url, thumbnail=thumbnail)
    
    if buffer_json['pager'] is not None:
        pattern_page = 'pg=([0-9]+)'
        pattern_total = '<ul class="pager" total="([0-9]+)"'
        pattern_genre = 'sort=([0-9]+)'
        last_page = int(lutil.find_first(buffer_json['pager'], pattern_total)) - 1
        next_page = int(lutil.find_first(params.get("url"), pattern_page)) + 1
        if last_page != next_page:
            genre = lutil.find_first(params.get("url"), pattern_genre)
            next_page_url = 'http://www.tv5mondeplus.com/get/videos?pg=%s&type=genre&sort=%s&loadpg=false&order=date' %  (next_page, genre)
            lutil.log('next_page=%s last_page=%s next_page_url="%s"' % (next_page, last_page, next_page_url))
            lutil.addDir(action="main_list", title=">> Page suivante", url=next_page_url)

    lutil.close_dir(pluginhandle)

# This function searchs on the web server (up to 2 times) in order to get the video link and then reproduces the video.
def play_video(params):
    lutil.log("tv5monde.play_video "+repr(params))

    buffer_link = lutil.carga_web(params.get("url"))
    pattern_player  = '<videoUrl>([^<]+)</videoUrl>.*?<appleStreamingUrl>([^<]*)</appleStreamingUrl>'
    smil_url, video_url = lutil.find_first(buffer_link, pattern_player)
    if video_url:
        lutil.log('tv5monde.play_video: We have found the URL of the video file: "%s" and going to play it!!' % video_url)
        return lutil.play_resolved_url(pluginhandle = pluginhandle, url = video_url)
    else:
        lutil.log('tv5monde.play: We did not find the video file URL because it is very old. We have to load the smil URL and get the info from there: "%s"' % smil_url)
        buffer_smil = lutil.carga_web(smil_url)
        pattern_smil = '<video src="(tv5mondeplus/hq/[^"]+)"'
        video_source = lutil.find_first(buffer_smil, pattern_smil)
        if video_source:
            video_smil = 'http://dlhd.tv5monde.com/%s' % video_source
            lutil.log('tv5monde.play_video: We have found the URL of the video file: "%s" and going to play it!!' % video_smil)
            return lutil.play_resolved_url(pluginhandle = pluginhandle, url = video_smil)
        else:
            lutil.log("tv5monde.play_video: We did not find the video file URL from the smil info. We cannot play it!!")
            lutil.showWarning("Cette video n'est plus disponible sur TV5 Monde")

# This function is the entry point to the plugin execution.
run()
