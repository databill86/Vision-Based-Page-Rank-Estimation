#include "ScreenshotHandler.h"

/**
 * ~ScreenshotHandler
 */
ScreenshotHandler::~ScreenshotHandler() {
    delete lastScreenshot;
}

/**
 *
 */
ScreenshotHandler::ScreenshotHandler(int renderHeight, int renderWidth, bool& quitMessageLoop) : quitMessageLoop(quitMessageLoop) {
    logger = Logger::getInstance();

    this->renderHeight = renderHeight;
    this->renderWidth = renderWidth;

    lastScreenshot = new unsigned char[renderHeight * renderWidth * 4];
}

/**
 * GetViewRect - Sets height and width of the given CefRect-instance
 * @param browser represents the current CefBrowser-instance
 * @param rect represents the CefRect-instance of the given CefBrowser-instance
 * @return This will return true.
 */
void ScreenshotHandler::GetViewRect(CefRefPtr<CefBrowser> browser, CefRect &rect) {
    rect = CefRect(0, 0, renderWidth, renderHeight);
}

/**
 *
 */
void ScreenshotHandler::OnPaint(CefRefPtr<CefBrowser> browser, PaintElementType type, const RectList &dirtyRects,
                                const void *buffer, int width, int height) {

    if(!quitMessageLoop)
        memcpy(lastScreenshot, buffer, sizeof(unsigned char) * height * width * 4);
}

/**
 * getScreenshot - Returns the last screenshot painted.
 *
 * @return Screenshot in size 4 Bytes * width of screenshot * height screenshot
 */
unsigned char* ScreenshotHandler::getScreenshot(){

    auto* screenshot = new unsigned char[renderHeight * renderWidth * 4];

    // copying, since lastScreenshot will be cleaned after destructor call
    for(int i = 0; i < renderHeight * renderWidth * 4; i++){
        *(screenshot + i) = *(lastScreenshot + i);
    }

    return screenshot;
}