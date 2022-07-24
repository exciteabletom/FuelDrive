#!/usr/bin/env python3
"""
First-time initalisation tasks
"""
import sql


def init_db():
    sql.Base.metadata.create_all(sql.engine)


def init():
    init_db()


if __name__ == "__main__":
    init()
