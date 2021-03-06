//
// Created by doktorgibson on 1/12/19.
//

#include "UrlDataModule.h"

DataBase *UrlDataModule::process(std::string url) {
    logger->info("Running URL-DataModule ..");

    logger->info("Requiring UI Thread ..");
    CEF_REQUIRE_UI_THREAD();

    if(!CefCurrentlyOn(TID_UI))
        throw "Not in UI Thread!";

    logger->info("Runnning in UI thread!");

    UrlCollection * urlCollection = new UrlCollection;
    bool quitMessageLoop = false;
    bool loadingFailed = false;
    size_t  totalSize = 0;
    string title = "null";

    CefRefPtr<UrlLoadHandler>    urlLoadHandler(new UrlLoadHandler(url));
    CefRefPtr<UrlRenderHandler>  urlRenderHandler(new UrlRenderHandler());
    CefRefPtr<UrlResponseFilter> urlResponseFilter(new UrlResponseFilter(&totalSize));
    CefRefPtr<UrlRequestHandler> urlRequestHandler(new UrlRequestHandler(urlResponseFilter));
    CefRefPtr<UrlDisplayHandler> urlDisplayHandler(new UrlDisplayHandler(&title));
    CefRefPtr <UrlClient> urlClient = new UrlClient(url, urlCollection, &quitMessageLoop, urlDisplayHandler, urlRequestHandler, urlRenderHandler, urlLoadHandler );


    CefWindowInfo cefWindowInfo;
    cefWindowInfo.SetAsWindowless(0);

    CefBrowserSettings browserSettings;
    browserSettings.windowless_frame_rate = 1;

    CefRefPtr<CefBrowser> browser = CefBrowserHost::CreateBrowserSync(cefWindowInfo, urlClient, url, browserSettings, NULL);

    std::thread loadingTimer([&](){
        int secondsSteps = 0;

        while(secondsSteps < 31){
            if(quitMessageLoop)
                return;

            std::this_thread::sleep_for(std::chrono::seconds(1));
            ++secondsSteps;
        }

       logger->info("Website timed out loading.");
       quitMessageLoop = true;
       loadingFailed = true;
    });

    while (!quitMessageLoop){
        CefDoMessageLoopWork();
    }

    loadingTimer.join();

    if(!loadingFailed){
        urlCollection->setSize(totalSize / 1024);
        urlCollection->setTitle(title);
    }

    browser->GetHost()->CloseBrowser(true);

    return urlCollection;
}
