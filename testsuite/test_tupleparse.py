# coding=utf-8

from pywbemReq.tupleparse import parse_reply_xml
from unittest import TestCase

__author__ = 'Ryan Liang'


class TestTupleparse(TestCase):

    def test_parse_reply_xml(self):
        reply_xml = '''<?xml version="1.0" encoding="utf-8" ?>
<CIM CIMVERSION="2.0" DTDVERSION="2.0"><MESSAGE ID="1001" PROTOCOLVERSION="1.0">
<SIMPLERSP><IMETHODRESPONSE NAME="GetInstance"><IRETURNVALUE><INSTANCE CLASSNAME="EMC_VNXe_ConcreteJobLeaf">
<PROPERTY NAME="InstanceID" TYPE="string"><VALUE>N-258</VALUE>
</PROPERTY>
<PROPERTY NAME="DeleteOnCompletion" TYPE="boolean"><VALUE>true</VALUE>
</PROPERTY>
<PROPERTY NAME="Description" TYPE="string"><VALUE>job.storagevolumeservice.job.Create</VALUE>
</PROPERTY>
<PROPERTY NAME="ElapsedTime" TYPE="datetime"><VALUE>00000000000019.064241:000</VALUE>
</PROPERTY>
<PROPERTY NAME="ErrorCode" TYPE="uint16"><VALUE>0</VALUE>
</PROPERTY>
<PROPERTY NAME="ErrorDescription" TYPE="string"><VALUE></VALUE>
</PROPERTY>
<PROPERTY NAME="JobState" TYPE="uint16"><VALUE>7</VALUE>
</PROPERTY>
<PROPERTY NAME="JobStatus" TYPE="string"><VALUE>Completed</VALUE>
</PROPERTY>
<PROPERTY NAME="LocalOrUtcTime" TYPE="uint16"><VALUE>2</VALUE>
</PROPERTY>
<PROPERTY NAME="MethodName" TYPE="string"><VALUE>EMC_VNXe_StorageConfigurationServiceLeaf.CreateOrModifyElementFromStoragePool</VALUE>
</PROPERTY>
<PROPERTY NAME="MethodReturnValue" TYPE="string"><VALUE>4096</VALUE>
</PROPERTY>
<PROPERTY NAME="MethodReturnValueType" TYPE="uint16"><VALUE>9</VALUE>
</PROPERTY>
<PROPERTY NAME="Name" TYPE="string"><VALUE>N-258</VALUE>
</PROPERTY>
<PROPERTY.ARRAY NAME="OperationalStatus" TYPE="uint16"><VALUE.ARRAY>
<VALUE>17</VALUE>
<VALUE>2</VALUE>
</VALUE.ARRAY>
</PROPERTY.ARRAY>
<PROPERTY NAME="PercentComplete" TYPE="uint16"><VALUE>100</VALUE>
</PROPERTY>
<PROPERTY.ARRAY NAME="PostAffectedJobElements" TYPE="string"><VALUE.ARRAY>
<VALUE>root/emc/smis:EMC_VNXe_StorageVolumeLeaf%CreationClassName=EMC_VNXe_StorageVolumeLeaf%DeviceID=sv_27%SystemCreationClassName=EMC_VNXe_StorageSystemLeaf%SystemName=FCNCH0972C3195</VALUE>
</VALUE.ARRAY>
</PROPERTY.ARRAY>
<PROPERTY.ARRAY NAME="PostCallMethodParameters" TYPE="string"><VALUE.ARRAY>
<VALUE>InPool</VALUE>
<VALUE>root/emc/smis:EMC_VNXe_MappedStoragePoolLeaf%InstanceID=FCNCH0972C3195+pool_5</VALUE>
<VALUE>ElementName</VALUE>
<VALUE>lun_2016-07-14T02:55:38.352144</VALUE>
<VALUE>ElementType</VALUE>
<VALUE>2</VALUE>
<VALUE>Size</VALUE>
<VALUE>1073741824</VALUE>
<VALUE>Job</VALUE>
<VALUE>root/emc/smis:EMC_VNXe_ConcreteJobLeaf%InstanceID=N-258</VALUE>
</VALUE.ARRAY>
</PROPERTY.ARRAY>
<PROPERTY.ARRAY NAME="PreAffectedJobElements" TYPE="string"><VALUE.ARRAY>
<VALUE>root/emc/smis:EMC_VNXe_MappedStoragePoolLeaf%InstanceID=FCNCH0972C3195+pool_5</VALUE>
</VALUE.ARRAY>
</PROPERTY.ARRAY>
<PROPERTY.ARRAY NAME="PreCallMethodParameters" TYPE="string"><VALUE.ARRAY>
<VALUE>InPool</VALUE>
<VALUE>root/emc/smis:EMC_VNXe_MappedStoragePoolLeaf%InstanceID=FCNCH0972C3195+pool_5</VALUE>
<VALUE>ElementName</VALUE>
<VALUE>lun_2016-07-14T02:55:38.352144</VALUE>
<VALUE>ElementType</VALUE>
<VALUE>2</VALUE>
<VALUE>Size</VALUE>
<VALUE>1073741824</VALUE>
</VALUE.ARRAY>
</PROPERTY.ARRAY>
<PROPERTY NAME="StartTime" TYPE="datetime"><VALUE>20160714065623.216401+000</VALUE>
</PROPERTY>
<PROPERTY.ARRAY NAME="StatusDescriptions" TYPE="string"><VALUE.ARRAY>
<VALUE>Completed</VALUE>
<VALUE>OK</VALUE>
</VALUE.ARRAY>
</PROPERTY.ARRAY>
<PROPERTY NAME="TimeBeforeRemoval" TYPE="datetime"><VALUE>00000000010000.000000:000</VALUE>
</PROPERTY>
<PROPERTY NAME="TimeOfLastStateChange" TYPE="datetime"><VALUE>20160714065642.280642+000</VALUE>
</PROPERTY>
<PROPERTY NAME="TimeSubmitted" TYPE="datetime"><VALUE>20160714065622.934786+000</VALUE>
</PROPERTY>
</INSTANCE>
</IRETURNVALUE></IMETHODRESPONSE></SIMPLERSP></MESSAGE></CIM>
'''

        parse_reply_xml(reply_xml)
