#include "mainwindowbis.h"
#include "ui_mainwindowbis.h"

MainWindowBIS::MainWindowBIS(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindowBIS)
{
    ui->setupUi(this);
}

MainWindowBIS::~MainWindowBIS()
{
    delete ui;
}
