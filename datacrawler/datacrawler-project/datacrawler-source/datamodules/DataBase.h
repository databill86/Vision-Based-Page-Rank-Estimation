#ifndef DATACRAWLER_PROJECT_DATABASE_H
#define DATACRAWLER_PROJECT_DATABASE_H


#include "../DataModulesEnum.h"

class DataBase {

public:
    virtual DataModulesEnum getDataModuleType();
    virtual ~DataBase();
};


#endif //DATACRAWLER_PROJECT_DATABASE_H