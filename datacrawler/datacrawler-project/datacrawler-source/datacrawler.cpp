#include "datacrawler.h"

/**
 * Datacrawler
 */
Datacrawler::Datacrawler() {
    logger = Logger::getInstance();
}

Datacrawler::~Datacrawler() {}

/**
 * init - Loads all user-defined DataModules and prepares Datacrawler to crawl given url
 */
void Datacrawler::init() {
    logger->info("Initialising Datacrawler !");

    logger->info("Loading general configuration!");
    numNodes = datacrawlerConfiguration.getNumNodes();

    logger->info("Number of nodes " + to_string(numNodes));

    if (datacrawlerConfiguration.getConfiguration(SCREENSHOT_MODULE) != nullptr) {
        dataModules.push_front(datacrawlerConfiguration.getConfiguration(SCREENSHOT_MODULE)->createInstance());
        logger->info("Using Screenshot-DataModule ..");
    }

    if (datacrawlerConfiguration.getConfiguration(SCREENSHOT_MOBILE_MODULE) != nullptr) {
        dataModules.push_front(datacrawlerConfiguration.getConfiguration(SCREENSHOT_MOBILE_MODULE)->createInstance());
        logger->info("Using ScreenshotMobile-DataModule ..");
    }

    if (datacrawlerConfiguration.getConfiguration(URL_MODULE) != nullptr) {
        dataModules.push_front(datacrawlerConfiguration.getConfiguration(URL_MODULE)->createInstance());
        logger->info("Using URL-Module ..");
    }

    logger->info("Initialising Datacrawler finished!");
}

/**
 * process - Process given url with loaded DataModules
 * @param url which should be processed
 * @return NodeElement which represents a node in the graph with all data the user defined for the graph
 */
map<string, NodeElement*>* Datacrawler::process(string url) {
    logger->info("Analysing start node!");
    logger->info("Processing <" + url + ">");
    logger->info("Running DataModules!");

    graph = new map<std::string, NodeElement*>;
    NodeElement * startNode = new NodeElement(true);
    UrlCollection * startNodeUrlCollection = nullptr;
    int tmpNumNodes = numNodes;

    for (DataModuleBase* x: dataModules) {
        startNode->addData(x->process(url));
        std::thread screenshotHandlerStopped([]() {
            std::this_thread::sleep_for(std::chrono::milliseconds(1000));
        });
        screenshotHandlerStopped.join();
    }

    logger->info("<" + url + "> processed!");

    for (DataBase* x: *startNode->getData()) {
        // get base url of starting node, which is different from domain name
        if (x->getDataModules() == URL_MODULE)
            startNodeUrlCollection = (UrlCollection*) x;
    }

    if (startNodeUrlCollection == nullptr) {
        // for single-node graphs, we use the passed url.
        graph->insert(make_pair(url, startNode));
        return graph;
    } else if (startNodeUrlCollection->getUrls()->empty()) {
        // for single-node graphs, we use the passed url.
        graph->insert(make_pair(url, startNode));
        return graph;
    }

    queue<pair<string, NodeElement*>> nodes;

    graph->insert(make_pair(startNodeUrlCollection->getBaseUrl(), startNode));
    nodes.push(make_pair(startNodeUrlCollection->getBaseUrl(), startNode));
    --numNodes;

    while(!nodes.empty()) {
        if(numNodes <= 0)
            break;

        vector<pair<string,NodeElement*>> newNodes = buildNodes(nodes.front().second);

        for(auto node: newNodes){
            graph->insert(node);
            nodes.push(node);
        }
        nodes.pop();
    }

   for(auto node : *graph){
      auto nodeData = node.second->getData();

      for(DataBase* entry : *nodeData){
          if(entry->getDataModules() != URL_MODULE)
              continue;
          ((UrlCollection*)entry)->deleteArbitaryEdges(graph);
      }
   }

   numNodes = tmpNumNodes;
   return graph;
}

vector<pair<string, NodeElement*>> Datacrawler::buildNodes(NodeElement* startNode) {
    UrlCollection *urlCollection;
    NodeElement *newNode;
    vector<pair<string,NodeElement*>> newNodes;

    for (DataBase * x: *startNode->getData()) {
       if (x->getDataModules() == URL_MODULE)
            urlCollection = (UrlCollection *) x;
    }

    vector<Url*>* urls = urlCollection->getUrls();
    for (Url * edge : *urls) {
        string edgeUrl = edge->getUrl();

        // check if exists in the graph
        if(graph->find(edgeUrl) != graph->end())
                continue;

        // check if we are allowed to generate more nodes
        if (numNodes <= 0)
            return newNodes;

        newNode = new NodeElement(false);

        // calculate new node
        for (DataModuleBase* x: dataModules) {
            newNode->addData(x->process(edgeUrl));
            std::thread screenshotHandlerStopped([]() {
                std::this_thread::sleep_for(std::chrono::milliseconds(1000));
            });
            screenshotHandlerStopped.join();
        }

        // insert into graph
        newNodes.push_back(make_pair(edgeUrl, newNode));
        --numNodes;
    }
    return newNodes;
}