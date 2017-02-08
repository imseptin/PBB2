# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ImportBidang
                                 A QGIS plugin
 Import bidang ke Basisdata Bidang
                             -------------------
        begin                : 2017-02-08
        copyright            : (C) 2017 by Septin Mulatsih Rezki
        email                : septinmulatsihrezki@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ImportBidang class from file ImportBidang.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .import_bidang import ImportBidang
    return ImportBidang(iface)
