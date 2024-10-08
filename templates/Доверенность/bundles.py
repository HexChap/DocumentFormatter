class NotaryBundle(BaseBundle):
    na_no: int = Field(description="Номер нот. акта")
    na_vol: str = Field(description="Том нот. акта")
    na_reg_no: int = Field(description="Номер регистрации нот. акта")
    na_case_no: int = Field(description="Номер дела нот. акта")
    na_date: common_fields.DateField = Field(description="Дата дела")
    notary_name: str = Field(description="Полное имя нотариуса, твор. падеж", examples=["Джоном Доевичом"])
    notary_loc: str = Field(description="Место деятельности нот.", examples=["Бургасский районный суд"])
    notary_reg_no: int = Field(description="Номер регистрации нот.")


bundles = [
    common_bundles.RusCitizenInfoBundle,
    common_bundles.BgResidentBundle,
    NotaryBundle,
    common_bundles.ObjectInfoBundle
]
