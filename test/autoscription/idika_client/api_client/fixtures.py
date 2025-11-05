import pytest


@pytest.fixture
def authenticated_response():
    return """
            <User>
                <pharmacy>
                    <id>12345</id>
                    <name>Example Pharmacy</name>
                    <!-- Other pharmacy information -->
                </pharmacy>
                <!-- Other user information -->
            </User>
            """


@pytest.fixture
def clinical_document_minimum_requirements():
    return """
        <ClinicalDocument xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:epsos="urn:epsos-org:ep:medication" xmlns="urn:hl7-org:v3">
            <id extension="1111111111111" root="1.21" />
            <effectiveTime xsi:type="IVL_TS">
                <low value="20150120" />
                <high value="20150130" />
            </effectiveTime>
            <author>
                <assignedAuthor>
                    <id extension="21" root="1.19.1"/>
                    <id extension="ΩΤΟΡΙΝΟΛΑΡΥΓΓΟΛΟΓΟΣ" root="1.19.2"/>
                </assignedAuthor>
            </author>
            <component>
                <structuredBody>
                    <component>
                        <section>
                            <text>
                                <list>
                                </list>
                            </text>
                            <entry>
                                <act>
                                    <id root="1.1.7" extension="1"/>
                                    <id root="1.1.8" extension="0"/>
                                    <id root="1.1.23" extension="1"/>
                                </act>
                            </entry>
                        </section>
                    </component>
                </structuredBody>
            </component>
            </ClinicalDocument>
        """


@pytest.fixture
def pharmacist_units_response():
    return """
    <List> <!-- based on idika sample, here https://testeps.e-prescription.gr/pharmacistapi/web/partials/3047425.html -->
    <timestamp>2015-09-04T16:59:22.624</timestamp>
    <contents>
        <item>
            <id>4</id>
            <healthCareUnit>
                <id>10</id>
                <unitType>
                    <id>2</id>
                    <name>Τεστ Φαρμακείο</name>
                </unitType>
                <description>Τεστ Φαρμακείο</description>
                <address />
                <telephone />
            </healthCareUnit>
            <startDate>2015-04-20 11:45:00</startDate>
            <expiryDate/>
            <description>Τεστ Φαρμακείο</description>
            <canPrescribeMed>true</canPrescribeMed>
            <canPrescribeExam>false</canPrescribeExam>
            <canExecuteExam>true</canExecuteExam>
            <pharmacy>
                <id>11073</id>
                <pharmacyTypeID>1</pharmacyTypeID>
                <name>ONOMA FARMAKEIOU 1</name>
                <companyType>
                    <id>4</id>
                    <name>ΕΤΕΡΟΡΡΥΘΜΟΣ ΕΤΑΙΡΕΙΑ</name>
                </companyType>
                <taxOffice>
                    <id>6</id>
                    <code>5454</code>
                    <name>Α ΘΕΣΣΑΛΟΝΙΚΗΣ  </name>
                </taxOffice>
                <taxRegistryNo>110022002</taxRegistryNo>
                <pharmacistUnion>
                    <id>2</id>
                    <address>ΧΑΡ.ΤΡΙΚΟΥΠΗ 1</address>
                    <postalCode>30200</postalCode>
                    <city>
                        <id>3598</id>
                        <name>ΜΕΣΟΛΟΓΓΙ</name>
                        <county>
                            <id>1</id>
                            <name>ΑΙΤΩΛΟΑΚΑΡΝΑΝΙΑΣ</name>
                            <country>
                                <Id>1</Id>
                                <name>ΕΛΛΑΔΑ</name>
                                <nameInEnglish>GREECE</nameInEnglish>
                                <code>EL</code>
                            </country>
                        </county>
                    </city>
                    <telephone>26310/26976</telephone>
                    <fax>26310/26976</fax>
                    <email />
                    <name>ΑΙΤΩΛ/ΝΙΑΣ</name>
                </pharmacistUnion>
                <pharmacistUnionRegNo>010</pharmacistUnionRegNo>
                <licenceNo>G333</licenceNo>
                <bank />
                <iban />
                <address>ΔΙΕΥΘ 5</address>
                <postalCode>43223</postalCode>
                <city>
                    <id>310</id>
                    <name>ΘΕΣΣΑΛΟΝΙΚΗ</name>
                    <county>
                        <id>19</id>
                        <name>ΘΕΣΣΑΛΟΝΙΚΗΣ</name>
                        <country>
                            <Id>1</Id>
                            <name>ΕΛΛΑΔΑ</name>
                            <nameInEnglish>GREECE</nameInEnglish>
                            <code>EL</code>
                        </country>
                    </county>
                </city>
                <telephone>2105414141</telephone>
                <adsl />
                <isIka>false</isIka>
                <isHospital>true</isHospital>
                <pharmacyIdentification>7766554433</pharmacyIdentification>
                <pharmacyType />
            </pharmacy>
        </item>
        <item> <!-- second item identical to the first, used to force xsdata to identify a list of items -->
            <id>4</id>
            <healthCareUnit>
                <id>10</id>
                <unitType>
                    <id>2</id>
                    <name>Τεστ Φαρμακείο</name>
                </unitType>
                <description>Τεστ Φαρμακείο</description>
                <address />
                <telephone />
            </healthCareUnit>
            <startDate>2015-04-20 11:45:00</startDate>
            <expiryDate>2017-04-20 00:00:00</expiryDate>
            <description>Τεστ Φαρμακείο</description>
            <canPrescribeMed>true</canPrescribeMed>
            <canPrescribeExam>false</canPrescribeExam>
            <canExecuteExam>true</canExecuteExam>
            <pharmacy>
                <id>11074</id>
                <pharmacyTypeID>1</pharmacyTypeID>
                <name>ONOMA FARMAKEIOU 2</name>
                <companyType>
                    <id>4</id>
                    <name>ΕΤΕΡΟΡΡΥΘΜΟΣ ΕΤΑΙΡΕΙΑ</name>
                </companyType>
                <taxOffice>
                    <id>6</id>
                    <code>5454</code>
                    <name>Α ΘΕΣΣΑΛΟΝΙΚΗΣ  </name>
                </taxOffice>
                <taxRegistryNo>110022002</taxRegistryNo>
                <pharmacistUnion>
                    <id>2</id>
                    <address>ΧΑΡ.ΤΡΙΚΟΥΠΗ 1</address>
                    <postalCode>30200</postalCode>
                    <city>
                        <id>3598</id>
                        <name>ΜΕΣΟΛΟΓΓΙ</name>
                        <county>
                            <id>1</id>
                            <name>ΑΙΤΩΛΟΑΚΑΡΝΑΝΙΑΣ</name>
                            <country>
                                <Id>1</Id>
                                <name>ΕΛΛΑΔΑ</name>
                                <nameInEnglish>GREECE</nameInEnglish>
                                <code>EL</code>
                            </country>
                        </county>
                    </city>
                    <telephone>26310/26976</telephone>
                    <fax>26310/26976</fax>
                    <email />
                    <name>ΑΙΤΩΛ/ΝΙΑΣ</name>
                </pharmacistUnion>
                <pharmacistUnionRegNo>010</pharmacistUnionRegNo>
                <licenceNo>G333</licenceNo>
                <bank />
                <iban />
                <address>ΔΙΕΥΘ 5</address>
                <postalCode>43223</postalCode>
                <city>
                    <id>310</id>
                    <name>ΘΕΣΣΑΛΟΝΙΚΗ</name>
                    <county>
                        <id>19</id>
                        <name>ΘΕΣΣΑΛΟΝΙΚΗΣ</name>
                        <country>
                            <Id>1</Id>
                            <name>ΕΛΛΑΔΑ</name>
                            <nameInEnglish>GREECE</nameInEnglish>
                            <code>EL</code>
                        </country>
                    </county>
                </city>
                <telephone>2105414141</telephone>
                <adsl />
                <isIka>false</isIka>
                <isHospital>true</isHospital>
                <pharmacyIdentification>7766554433</pharmacyIdentification>
                <pharmacyType />
            </pharmacy>
        </item>
    </contents>
    <count>2</count>
</List>
"""
