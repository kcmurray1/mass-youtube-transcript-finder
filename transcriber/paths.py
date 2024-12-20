
class Paths:
    """Paths to elements used by Selenium"""

    XPATH_VIDEO_COUNT = "/html[1]/body[1]/ytd-app[1]/div[1]/ytd-page-manager[1]/ytd-browse[1]/div[3]/ytd-tabbed-page-header[1]/tp-yt-app-header-layout[1]/div[1]/tp-yt-app-header[1]/div[2]/div[1]/div[2]/yt-page-header-renderer[1]/yt-page-header-view-model[1]/div[1]/div[1]/div[1]/yt-content-metadata-view-model[1]/div[2]/span[3]/span[1]"
    # XPATH_BUTTON_TRANSCRIPT = "//ytd-structured-description-content-renderer[@id='structured-description']//ytd-video-description-transcript-section-renderer[@class='style-scope ytd-structured-description-content-renderer']//div[@class='yt-spec-touch-feedback-shape__fill']"
    XPATH_BUTTON_TRANSCRIPT = "//ytd-watch-metadata//ytd-video-description-transcript-section-renderer//ytd-button-renderer//button"
    # XPATH_BUTTON_DESCRIPTION = "//tp-yt-paper-button[@id='expand']" Outdated 12/20/24
    XPATH_BUTTON_DESCRIPTION = "(//tp-yt-paper-button[@id='expand'])[2]"


    ID_VIDEO_COUNT = "videos-count" # Outdated 7/5/24
    ID_VIDEO = "video-title-link"
    ID_PLAYLIST_VIDEO = "wc-endpoint"
    ID_PLAYLIST_VIDEO_TITLE = "video-title"

    CSS_TEXT_TRANSCRIPT = "div[class='segment style-scope ytd-transcript-segment-renderer']"

