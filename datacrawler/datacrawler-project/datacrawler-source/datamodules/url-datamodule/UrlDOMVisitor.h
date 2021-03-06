//
// Created by doktorgibson on 1/13/19.
//

#ifndef DATACRAWLER_PROJECT_URLDOMVISITOR_H
#define DATACRAWLER_PROJECT_URLDOMVISITOR_H


#include <include/cef_dom.h>
#include "../../util/Logger.h"

#include "iostream"
#include <queue>
#include <regex>
#include <chrono>
#include "Url.h"

using namespace std;

class UrlDOMVisitor : public CefDOMVisitor {
private:
    IMPLEMENT_REFCOUNTING(UrlDOMVisitor)
    Logger *logger;
    string url;
    string baseUrl;
    string baseUrlDomainOnly;

    vector<pair<string,string>>& validUrls;
    map<string, string> validUrlMap;

    queue<CefRefPtr<CefDOMNode>> traverseDOMTree(CefRefPtr<CefDOMNode>);
    void filterURL(queue<CefRefPtr<CefDOMNode>>&);
    void shuffleURLs();

public:
    void Visit(CefRefPtr<CefDOMDocument>) OVERRIDE;

    UrlDOMVisitor(vector<pair<string,string>>&, string);
    ~UrlDOMVisitor();
};


#endif //DATACRAWLER_PROJECT_URLDOMVISITOR_H
