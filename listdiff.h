#ifndef LISTDIFF_H
#define LISTDIFF_H

#include <QWidget>

namespace Ui {
class ListDiff;
}

class ListDiff : public QWidget
{
    Q_OBJECT

public:
    explicit ListDiff(QWidget *parent = 0);
    ~ListDiff();

private:
    Ui::ListDiff *ui;
};

#endif // LISTDIFF_H
