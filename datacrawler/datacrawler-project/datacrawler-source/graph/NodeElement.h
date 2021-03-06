#ifndef DATACRAWLER_PROJECT_NODEELEMENT_H
#define DATACRAWLER_PROJECT_NODEELEMENT_H

#include <list>

#include "../datamodules/DataBase.h"

class NodeElement {

private:
   std::vector<DataBase*> data;
   bool startNode;

public:
    void addData(DataBase*);
    std::vector<DataBase*>* getData();
    bool isStartNode();

    NodeElement(bool);
    ~NodeElement();
};


#endif //DATACRAWLER_PROJECT_NODEELEMENT_H
