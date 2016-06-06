#include "listdiff.h"
#include "ui_listdiff.h"

ListDiff::ListDiff(QWidget *parent) :
    QWidget(parent),
    ui(new Ui::ListDiff)
{
    ui->setupUi(this);
}

ListDiff::~ListDiff()
{
    delete ui;
}
