# Mapped idika prescription elements 
## asthenis
```json
{
    "1.10.1": "ΑΜΚΑ Ασθενή",
    "1.10.30.1": "Id Ασφαλιστικού Φορέα με βάση το οποίο έγινε η συνταγογράφηση",
    "1.10.30.2": "Όνομα Ασφαλιστικού Φορέα με βάση το οποίο έγινε η συνταγογράφηση",
    "1.10.2": "ΑΜΑ με βάση το οποίο έγινε η συνταγογράφηση",
    "1.20.1": "Τύπος ασφαλισμένου με βάση το οποίο έγινε η συνταγογράφηση",
    "1.30.1": "Ημερομηνία Τελευταίας Ενημέρωσης Ασφαλιστικού φορέα",
    "1.30.2": "Ημερομηνία Λήξης Ασφαλιστικής Ικανότητας",
    "1.40.1": "Ένδειξη ότι ο ασθενής έχει δηλώσει να λαμβάνει ηλεκτρονικά τις συνταγές του"
}
{
    "1.10.1": "patient_amka",
    "1.10.30.1": "prescribing_insurer_id",
    "1.10.30.2": "prescribing_insurer_name",
    "1.10.2": "prescribing_ama",
    "1.20.1": "insured_type",
    "1.30.1": "last_update_date_of_insurer",
    "1.30.2": "insurance_capability_expiry_date",
    "1.40.1": "indication_that_patient_has_declared_to_receive_prescriptions_electronically"
}
```
## assigned author
```json
{
    "1.18": "Id Γιατρού",
    "1.19": "ΑΜΚΑ Γιατρού",
    "1.19.1": "Id Ειδικότητας Ιατρού",
    "1.19.2": "Ονομασία Ειδικότητας Ιατρού",
    "1.20": "ETAA Γιατρού"
}
{
    "1.18": "doctor_id",
    "1.19": "doctor_amka",
    "1.19.1": "doctor_specialty_id",
    "1.19.2": "doctor_specialty_name",
    "1.20": "doctor_etee"
}
```
# assigned Entity
```json
{
    "1.18": "Id Γιατρού"
}
```

# barcode
```json
{
    "1.21": "Το barcode της Συνταγής (Extension: 1111111111111)"
}
```

# visit
```json
{
  "1.80": "visit_id",
  "1.80.1": "unit_of_prescription_id",
  "1.80.2": "insurance_carrier_id",
  "1.80.3": "comments",
  "1.80.3.1" :"reason_for_visit",
  "1.80.4" : "visit_within_limit"
}
```

# suntagi
```json
{
  "1.22": "Id Συνταγής",
  "1.1.3": "Τύπος Συνταγής 1:Τυπική | 2:Ελεύθερη",
  "1.1.4": "Έπαναληψιμότητα Συνταγής, 1:Απλή | 3: 3μηνη | 4: 4μηνη | 5: 5μηνη | 6: 6μηνη",
  "1.1.4.1": "Σε περίπτωση Έπαναληψιμότητας Συνταγής ποια είναι η σειρά της συνταγής αυτής 1, 2, 3, 4, 5, 6",
  "1.1.4.2": "Βarcode πρώτης (αρχικής) συνταγής σε περίπτωση Έπαναληψιμότητας Συνταγής",
  "1.1.4.3": "Ημερομηνία Έναρξης Ισχύος για Συνταγή που Επαναλαμβάνεται",
  "1.1.4.4": "Η Περίοδος Επανάληψης σε περίπτωση Επαναλαμβανόμενης Συνταγής 1: 30 ημέρες | 2: 28 ημέρες | 3: 60 ημέρες",
  "1.1.3.1": "Συνταγογραφημένη με βάση εμπορική ονομασία φαρμάκου",
  "1.1.3.2": "Id λόγου συνταγογράφησης με βάση την εμπορική ονομασία",
  "1.1.3.3": "Id σχολίων του λόγου συνταγογράφησης με βάση την εμπορική ονομασία",
  "1.1.6": "Ιd περίπτωσης μηδενικής συμμετοχής",
  "1.1.23": "Γνωμάτευση, 1:Ναι | 0:Όχι",
  "1.1.23.1": "ΑΜΚΑ Ιατρού Γνωμάτευσης",
  "1.1.23.2": "Ημερομηνία Γνωμάτευσης",
  "1.1.23.3": "Id Ειδικότητας Ιατρού Γνωμάτευσης",
  "1.1.23.4": "Ονομασία Ειδικότητας Ιατρού Γνωμάτευσης",
  "1.1.23.5": "Ονοματεπώνυμο Ιατρού Γνωμάτευσης",
  "1.1.23.6": "Barcode Ηλεκτρονικής Γνωμάτευσης",
  "1.4.11": "Μονοδοσιακό, 1:Ναι | 0:Όχι",
  "1.1.7": "Φάρμακο υψηλού κόστους",
  "1.1.30": "Φάρμακο με ηπαρίνη",
  "1.1.34": "Φάρμακο εισαγωγής ΙΦΕΤ",
  "1.1.8": "Εμβόλιο Απευαισθητοποίησης",
  "1.1.9": "Εκτελείται μόνο από φαρμακείο του ΕΟΠΥΥ",
  "1.1.10": "Εκτέλεση συνταγών ορισμένης κατηγορίας μόνο από ειδικά φαρμακεία και υπό προυποθέσεις",
  "1.1.11": "Περιέχει ναρκωτική ουσία",
  "1.1.11.1": "Kατηγορία ναρκωτικών συνταγής",
  "1.1.12": "Kαταχωρείται μόνο από Νοσοκομεία",
  "1.1.13": "Ειδικό Αντιβιοτικό",
  "1.1.14": "Σύμφωνα με το Nόμο 3816",
  "1.1.15": "I.Φ.Ε.Τ.",
  "1.1.16": "Απαιτείται προέγκριση Ε.Ο.Π.Υ.Υ. μέσω επιτροπής",
  "1.1.17": "Εκτός Φαρμακευτικής Δαπάνης ΕΟΠΥΥ",
  "1.1.18": "Περίπτωση εκτέλεσης",
  "1.1.19": "Πλήθος εκτελέσεων συνταγής",
  "1.1.19.1": "Οι ενεργές συνταγές",
  "1.1.2.1": "Ποσό συμμετοχής ασφαλιστικού φορέα του ασθενή για μηδενική συμμετοχή",
  "1.1.2.2": "Ποσό συμμετοχής ασφαλιστικού φορέα του ασθενή για συμμετοχή με ποσοστό 10%",
  "1.1.2.3": "Ποσό συμμετοχής ασφαλιστικού φορέα του ασθενή για συμμετοχή με ποσοστό  25%",
  "1.1.2.4": "Συνολικό ποσό συμμετοχής ασθενή",
  "1.1.2.4.1": "Συνολικό Ποσό Τιμών Αναφοράς",
  "1.2.1.4": "Συνολικό Ποσό διαφοράς Ασφαλιστικού Φορέα",
  "1.2.1.5": "Συνολικό Ποσό διαφοράς",
  "1.2.1.6": "Συνολικό Ποσό Διαφοράς Ασφαλισμένου",
  "1.1.2.5": "Συνολικό ποσό συμμετοχής Ασφαλιστικού Φορέα",
  "1.1.2.6": "Ποσό συμμετοχής ασθενή για μηδενική συμμετοχή",
  "1.1.2.7": "Ποσό συμμετοχής ασθενή για συμμετοχή με ποσοστό 10%",
  "1.1.2.8": "Ποσό συμμετοχής ασθενή για συμμετοχή με ποσοστό 25%",
  "1.1.20": "Barcode χειρόγραφης συνταγής",
  "1.1.21": "Δεν καλύπτεται από ασφαλιστικό ταμείο",
  "1.1.22.2": "Επιβάρυνση από ασφαλιστικό ταμείο (Επιβάρυνση 1 Ευρώ) - Αν η συνταγή επιβαρυνθεί ή όχι",
  "1.1.22": "Ποσό Επιβάρυνσης από ασφαλιστικό ταμείο (Επιβάρυνση 1 Ευρώ)",
  "1.1.22.1": "Επιβάρυνση από ασφαλιστικό ταμείο (Επιβάρυνση 1 Ευρώ) - Αν η συνταγή έχει επιβαρυνθεί ή όχι",
  "1.1.24": "Ένδειξη συνταγής με εμβόλια | 0 : Η συνταγή περιέχει φάρμακα - 1 : Η συνταγή περιέχει εμβόλια",
  "1.1.25": "Ένδειξη συνταγής που έχει δεσμευτεί ή όχι | 1 : Η συνταγή έχει δεσμευτεί - 0 : Η συνταγή δεν έχει δεσμευτεί",
  "1.1.26": "Ένδειξη απαλλαγής συμμετοχής ασφαλισμένου | 1 : Ναι | 0 : Όχι",
  "1.1.26.1": "Λόγος απαλλαγής συμμετοχής ασφαλισμένου",
  "1.1.27": "Ένδειξη ότι ασφαλιστικός φορέας καλύπτει συμπληρωματικά την συμμετοχή του ασφαλισμένου | 1 : Ναι | 0 : Όχι",
  "1.1.27.1": "Το συνολικό ποσό συμπληρωματικής κάλυψης συμμετοχής ασφαλισμένου από τον ασφαλιστικό φορέα (ΤΕΑΠΑΣΑ)",
  "1.1.27.2": "Συνολικό ποσό διαφοράς που καλύπτεται από τον ΚΥΥΑΠ",
  "1.1.28.1": "Ένδειξη αν η συνταγή έχει φάρμακα αρνητικής λίστας",
  "1.1.29": "Περιέχει αντιβιοτικό φάρμακο",
  "1.8.1": "Συνταγή με Αναλώσιμα - Για extension = 0 Η συνταγή περιέχει μόνο φάρμακα",
  "1.80": "Id Επίσκεψης",
  "1.5.10": "Ένδειξη ότι η συνταγή είναι άυλη",
  "1.1.28": "Η Συνταγή περιέχει φάρμακα κατ’ οίκον παράδοσης",
  "1.5.13": "Πρόθεση/Επιθυμία ασθενούς για κατ’ οίκον παράδοση φαρμάκων, 1: Ναι | 0: Όχι"
}
{
  "1.22": "prescription_id",
  "1.1.3": "prescription_type_1_typical_2_free",
  "1.1.4": "prescription_repetition_1_simple_3_3_months_4_4_months_5_5_months_6_6_months",
  "1.1.4.1": "sequence_of_repeated_prescription",
  "1.1.4.2": "barcode_of_first_initial_prescription_in_case_of_repetition",
  "1.1.4.3": "start_date_of_validity_for_repeated_prescription",
  "1.1.4.4": "repetition_period_in_case_of_repeated_prescription_1_30_days_2_28_days_3_60_days",
  "1.1.3.1": "prescribed_based_on_commercial_name_of_drug",
  "1.1.3.2": "prescription_reason_id_based_on_commercial_name",
  "1.1.3.3": "comments_reason_id_based_on_commercial_name",
  "1.1.6": "zero_participation_case_id",
  "1.1.23": "consultation_indicator_1_yes_0_no",
  "1.1.23.1": "AMKA_of_consultation_doctor",
  "1.1.23.2": "consultation_date",
  "1.1.23.3": "specialty_id_of_consultation_doctor",
  "1.1.23.4": "name_of_specialty_of_consultation_doctor",
  "1.1.23.5": "full_name_of_consultation_doctor",
  "1.1.23.6": "barcode_of_electronic_consultation",
  "1.4.11": "single_dose_1_yes_0_no",
  "1.1.7": "high_cost_drug",
  "1.1.30": "heparin_drug",
  "1.1.34": "IFET_drug_entry",
  "1.1.8": "Desensitization_Vaccine",
  "1.1.9": "Performed_only_by_EOPYY_pharmacy",
  "1.1.10": "Execution_of_prescriptions_of_a_specific_category_only_by_special_pharmacies_and_under_conditions",
  "1.1.11": "Contains_narcotic_substance",
  "1.1.11.1": "Category_of_narcotic_prescription",
  "1.1.12": "Registered_only_by_Hospitals",
  "1.1.13": "Special_Antibiotic",
  "1.1.14": "According_to_Law_3816",
  "1.1.15": "IFET",
  "1.1.16": "Approval_required_by_EOPYY_through_committee",
  "1.1.17": "Outside_EOPYY_Pharmaceutical_Expense",
  "1.1.18": "Execution_case",
  "1.1.19": "Number_of_prescription_executions",
  "1.1.19.1": "Active_prescriptions",
  "1.1.2.1": "Patient_insurer_participation_amount_for_zero_participation",
  "1.1.2.2": "Patient_insurer_participation_amount_with_10_percent_participation",
  "1.1.2.3": "Patient_insurer_participation_amount_with_25_percent_participation",
  "1.1.2.4": "Total_patient_participation_amount",
  "1.1.2.4.1": "Total_Reference_Price_Amount",
  "1.2.1.4": "Total_Insurer_Difference_Amount",
  "1.2.1.5": "Total_Difference_Amount",
  "1.2.1.6": "Total_Insured_Difference_Amount",
  "1.1.2.5": "Total_Insurer_Participation_Amount",
  "1.1.2.6": "Patient_participation_amount_for_zero_participation",
  "1.1.2.7": "Patient_participation_amount_with_10_percent_participation",
  "1.1.2.8": "Patient_participation_amount_with_25_percent_participation",
  "1.1.20": "Barcode_of_handwritten_prescription",
  "1.1.21": "Not_covered_by_insurance_fund",
  "1.1.22.2": "Burden_from_insurance_fund_Burden_1_Euro_Whether_the_prescription_is_burdened_or_not",
  "1.1.22": "Amount_of_Burden_from_insurance_fund_Burden_1_Euro",
  "1.1.22.1": "Burden_from_insurance_fund_Burden_1_Euro_Whether_the_prescription_is_burdened_or_not",
  "1.1.24": "Indication_that_the_prescription_contains_vaccines_0_The_prescription_contains_drugs_1_The_prescription_contains_vaccines",
  "1.1.25": "Indication_whether_the_prescription_is_reserved_or_not_1_The_prescription_is_reserved_0_The_prescription_is_not_reserved",
  "1.1.26": "Indication_of_insured_participation_exemption_1_Yes_0_No",
  "1.1.26.1": "Reason_for_insured_participation_exemption",
  "1.1.27": "Indication_that_insurer_covers_supplementary_participation_of_insured_1_Yes_0_No",
  "1.1.27.1": "Total_amount_of_supplementary_coverage_of_insured_participation_by_insurer_TEAPASA",
  "1.1.27.2": "Total_amount_of_difference_covered_by_KYYAP",
  "1.1.28.1": "Indication_whether_the_prescription_contains_drugs_from_negative_list",
  "1.1.29": "Contains_antibiotic_drug",
  "1.8.1": "Prescription_with_Consumables_For_extension_0_The_prescription_contains_only_drugs",
  "1.80": "Visit_id",
  "1.5.10": "Indication_that_the_prescription_is_virtual",
  "1.1.28": "The_Prescription_contains_drugs_for_home_delivery",
  "1.5.13": "Patient's_intention_desire_for_home_delivery_of_drugs_1_Yes_0_No"
}
```
# farmako
```json
{
  "1.7.5.1": "Barcode Φαρμάκου",
  "1.7.5.2": "Εμπορική ονομασία φαρμάκου",
  "1.8.5.1": "Λιανική τιμή Φαρμάκου",
  "1.8.6.1": "Προηγούμενη Λιανική τιμή Φαρμάκου",
  "1.8.7.1": "Μειωμένη Λιανική τιμή Φαρμάκου",
  "1.8.5.2": "Τιμή Αναφοράς Φαρμάκου",
  "1.8.6.2": "Προηγούμενη Τιμή Αναφοράς Φαρμάκου",
  "1.8.7.2": "Μειωμένη Τιμή Αναφοράς Φαρμάκου",
  "1.8.5.3": "Τιμή Χονδρικής Φαρμάκου",
  "1.8.5.4": "Ειδική Τιμή Χονδρικής Φαρμάκου",
  "1.8.5.5": "Νοσοκομειακό Φάρμακο, 1: Ναι | 0: Όχι",
  "1.8.5.6": "Τιμή Νοσοκομείου για το φάρμακο",
  "1.9.5.1": "LOWER_PRICE 1: Ναι | 0: Όχι (ένδειξη χαμηλότερης τιμής ομοειδών φαρμάκων)",
  "1.9.6.1": "Τύπος Φαρμάκου",
  "1.9.6.2": "Θεραπευτική κατηγορία με γενόσημο,  1: Ναι | 0: Όχι",
  "1.9.7.1": "Ποσοστό της έκπτωσης συμμετοχής",
  "1.9.7.2": "Μήνυμα πληροφόρησης (Η ποσότητα αναφέρεται σε δεκάδες κατά αντιστοιχία με την ταινία γνησιότητας, π.χ. ποσότητα 2 αντιστοιχεί σε εκτέλεση 2 x 10 = 20 φυσίγγων του σκευάσματος)"
}
{
  "1.7.5.1": "drug_barcode",
  "1.7.5.2": "commercial_name_of_drug",
  "1.8.5.1": "retail_price_of_drug",
  "1.8.6.1": "previous_retail_price_of_drug",
  "1.8.7.1": "reduced_retail_price_of_drug",
  "1.8.5.2": "reference_price_of_drug",
  "1.8.6.2": "previous_reference_price_of_drug",
  "1.8.7.2": "reduced_reference_price_of_drug",
  "1.8.5.3": "wholesale_price_of_drug",
  "1.8.5.4": "special_wholesale_price_of_drug",
  "1.8.5.5": "hospital_drug",
  "1.8.5.6": "hospital_price_for_drug",
  "1.9.5.1": "lower_price_indication_of_homogeneous_drugs_yes_or_no",
  "1.9.6.1": "drug_type",
  "1.9.6.2": "therapeutic_category_with_generic",
  "1.9.7.1": "participation_discount_percentage",
  "1.9.7.2": "information_message_quantity_in_tens_corresponding_to_authenticity_tape_eg_quantity_2_corresponds_to_execution_2_x_10_20_units_of_the_drug"
}
```
        
# genosimo
```json
{
  "1.4.15": "Ένδειξη Πρότασης Γενοσήμου Φαρμάκου για τη θεραπεία (γραμμή συνταγής), 1: Ναι | 0: Όχι",
  "1.4.17": "Συνολικό ποσό τιμών αναφοράς",
  "1.4.18": "Ποσοστό συμμετοχής ασφαλισμένου",
  "1.4.19": "Υπόλοιπο",
  "1.4.20": "Συμμετοχή ασφαλισμένου",
  "1.4.21": "Διαφορά Συμμετοχής Ασφαλισμένου (Συνολική Διαφορά - Διαφορά Ασφαλ. Φορέα)",
  "1.4.21.1": "Συνολική Διαφορά της γραμμής Συνταγής (η οποία μερίζεται σε Ασφαλ. Φορέα και Ασφαλισμένο)",
  "1.4.21.3": "Διαφορά Ασφαλιστικού Φορέα",
  "1.4.22": "Στην περίπτωση συνταγογράφησης με βάση τη δραστική ουσία του φαρμάκου - Id λίστας ομοειδών φαρμάκων",
  "1.4.23": "Επιτρέπεται αντικατάσταση του φαρμάκου, 1: Ναι | 0: Όχι",
  "1.4.24": "Id Ασθένειας Συνταγής",
  "1.4.24.1": "Περιγραφή Ασθένειας Συνταγής",
  "1.4.24.2": "Προτεινόμενο ποσοστό ασθένειας",
  "1.4.25": "Στην περίπτωση συνταγογράφησης με βάση τη δραστική ουσία του φαρμάκου - Δραστική ουσία φαρμάκου εισαγωγής ΙΦΕΤ",
  "1.4.26": "Στην περίπτωση συνταγογράφησης με βάση τη δραστική ουσία του φαρμάκου - Φαρμακευτική μορφή φαρμάκου εισαγωγής ΙΦΕΤ",
  "1.4.27": "Στην περίπτωση συνταγογράφησης με βάση τη δραστική ουσία του φαρμάκου - Περιεκτικότητα φαρμάκου εισαγωγής ΙΦΕΤ",
  "1.4.28": "Στην περίπτωση συνταγογράφησης με βάση τη δραστική ουσία του φαρμάκου - Εμπορική ονομασία φαρμάκου εισαγωγής ΙΦΕΤ Φαρμακοποιού",
  "1.4.29": "Στην περίπτωση συνταγογράφησης με βάση τη δραστική ουσία του φαρμάκου - Μονάδα δόσης φαρμάκου εισαγωγής ΙΦΕΤ Φαρμακοποιού",
  "1.4.30": "Στην περίπτωση συνταγογράφησης με βάση τη δραστική ουσία του φαρμάκου - Φαρμακευτική μορφή φαρμάκου εισαγωγής ΙΦΕΤ Φαρμακοποιού",
  "1.4.31": "Στην περίπτωση συνταγογράφησης με βάση τη δραστική ουσία του φαρμάκου - Περιεκτικότητα φαρμάκου εισαγωγής ΙΦΕΤ Φαρμακοποιού",
  "1.4.32": "Στην περίπτωση συνταγογράφησης με βάση τη δραστική ουσία του φαρμάκου - Συσκευασία φαρμάκου εισαγωγής ΙΦΕΤ Φαρμακοποιού",
  "1.4.33": "Στην περίπτωση συνταγογράφησης με βάση τη δραστική ουσία του φαρμάκου - Τιμή Μονάδος φαρμάκου εισαγωγής ΙΦΕΤ Φαρμακοποιού"
}
{
  "1.4.15": "indication_of_generic_drug_proposal_for_treatment_on_prescription_line",
  "1.4.17": "total_reference_values_amount",
  "1.4.18": "percentage_of_insured_participation",
  "1.4.19": "balance",
  "1.4.20": "insured_participation",
  "1.4.21": "insured_participation_difference_insurer_difference_total_difference_insurer",
  "1.4.21.1": "total_difference_of_prescription_line_shared_between_insurer_and_insured",
  "1.4.21.3": "insurer_difference",
  "1.4.22": "in_case_of_prescribing_based_on_the_active_substance_of_the_drug_id_of_the_homogeneous_drug_list",
  "1.4.23": "replacement_of_the_drug_allowed",
  "1.4.24": "prescription_disease_id",
  "1.4.24.1": "prescription_disease_description",
  "1.4.24.2": "recommended_percentage_of_disease",
  "1.4.25": "in_case_of_prescribing_based_on_the_active_substance_of_the_drug_active_substance_of_the_drug_entry_ipet",
  "1.4.26": "in_case_of_prescribing_based_on_the_active_substance_of_the_drug_pharmaceutical_form_of_the_drug_entry_ipet",
  "1.4.27": "in_case_of_prescribing_based_on_the_active_substance_of_the_drug_content_of_the_drug_entry_ipet",
  "1.4.28": "in_case_of_prescribing_based_on_the_active_substance_of_the_drug_commercial_name_of_the_drug_entry_ipet_pharmacist",
  "1.4.29": "in_case_of_prescribing_based_on_the_active_substance_of_the_drug_dose_unit_of_the_drug_entry_ipet_pharmacist",
  "1.4.30": "in_case_of_prescribing_based_on_the_active_substance_of_the_drug_pharmaceutical_form_code_of_the_drug_entry_ipet_pharmacist",
  "1.4.31": "in_case_of_prescribing_based_on_the_active_substance_of_the_drug_content_of_the_drug_entry_ipet_pharmacist",
  "1.4.32": "in_case_of_prescribing_based_on_the_active_substance_of_the_drug_package_of_the_drug_entry_ipet_pharmacist",
  "1.4.33": "in_case_of_prescribing_based_on_the_active_substance_of_the_drug_unit_price_of_the_drug_entry_ipet_pharmacist"
}
```


# Execution Details
```json
{
  "2.10.6": "Συναίνεση Ασθενή",
  "2.10.8": "Πλήθος εκτέλεσης φαρμάκου",
  "2.10.9": "Τιμή Εκτέλεσης",
  "2.10.11": "Τιμή Αναφοράς",
  "2.10.10": "Τιμή Λιανικής",
  "2.10.12": "Ταινία γνησιότητας",
  "1.4.21.2": "Διαφορά Ασφαλιστικού Φορέα ανά Εκτέλεση Ποσότητας Φαρμάκου"
}
{
  "2.10.6":  "consent_patient",
  "2.10.8":  "execution_quantity",
  "2.10.9": "execution_price",
  "2.10.11": "reference_price",
  "2.10.10": "retail_price",
  "2.10.12": "authenticity_tape",
  "1.4.21.2": "insurer_difference_per_execution_quantity"
}
```