//
// Created by Samed Güner on 18.10.18.
//

#ifndef EXPERIMENT_PROJECT_EXPERIMENT_HANDLER_H
#define EXPERIMENT_PROJECT_EXPERIMENT_HANDLER_H


#include <include/cef_render_handler.h>
#include <include/cef_client.h>
#include "iostream"

class ExperimentHandler : public CefRenderHandler {

private:
    int renderWidth;
    int renderHeight;

public:
    ExperimentHandler(){
        renderWidth = 800;
        renderHeight = 600;
    };

    ExperimentHandler(int width, int height){
        renderWidth = width;
        renderHeight = height;
    }

    // Override CefRenderHandler methods
    bool GetViewRect(CefRefPtr<CefBrowser> browser, CefRect &rect) OVERRIDE {
        rect = CefRect(0, 0, renderWidth, renderHeight);
        return true;
    }

    void OnPaint(CefRefPtr<CefBrowser> browser, PaintElementType type, const RectList &dirtyRects, const void *buffer,
                 int width, int height) OVERRIDE {
        unsigned char* img = (unsigned char*)buffer;
        printf("frame rendered (pixel[0]: (%d %d %d - %d)\n", img[2], img[1], img[0], img[3]);
        printf("frame rendered (pixel[1]: (%d %d %d - %d)\n", img[6], img[5], img[4], img[7]);
        printf("width: %d height: %d\n", width, height);

    }

private:
    IMPLEMENT_REFCOUNTING(ExperimentHandler);

};


#endif //EXPERIMENT_PROJECT_EXPERIMENT_HANDLER_H
