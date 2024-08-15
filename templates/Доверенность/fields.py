class NotaryBundle(BaseModel):
    na_no: int = Field(description="Номер нот. акта")
    na_vol: str = Field(description="Том нот. акта")
    na_reg_no: int = Field(description="Номер регистрации нот. акта")
    na_case_no: int = Field(description="Номер дела нот. акта")
    na_date: base_bundles.DateField = Field(description="Дата дела")
    notary_name: str = Field(description="Полное имя нотариуса", examples=["Джон Доевич"])
    notary_loc: str = Field(description="Место деятельности нот.", examples=["Бургасский районный суд"])
    notary_reg_no: int = Field(description="Номер регистрации нот.")


fields = [
    base_bundles.RepeatableRusCitizenInfoBundle,
    NotaryBundle,
    base_bundles.Num2WordedObjectInfoBundle
]
